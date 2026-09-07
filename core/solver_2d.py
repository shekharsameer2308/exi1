#
# Copyright 2026 Membrane-Reactor-SciML Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
2D Axisymmetric Heterogeneous Catalytic Membrane Reactor (CMR) Solver.
Integrates coupled 2D PDE system with Maxwell-Stefan mass extraction at the inner membrane wall.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from core.kinetics import calculate_mignard_pritchard_rates, check_catalyst_stability
from core.maxwell_stefan import compute_maxwell_stefan_flux
from core.thermodynamics import R_GAS


@dataclass
class ReactorConfig:
    """Configuration dataclass for 2D Heterogeneous Annular Reactor."""

    length_m: float = 0.25  # 250 mm
    d_wall_m: float = 0.020  # 20 mm outer wall
    d_membrane_m: float = 0.010  # 10 mm inner membrane
    rho_bed_kg_m3: float = 1150.0
    bed_voidage: float = 0.40
    d_pellet_m: float = 0.003

    # Operating
    T_op_K: float = 523.15  # 250 °C
    P_ret_Pa: float = 100.0e5  # 100 bar
    P_perm_Pa: float = 1.0e5  # 1 bar (delta_P = 99 bar)
    GHSV_h: float = 500.0  # h^-1 STP
    feed_h2_co2_ratio: float = 3.0
    is_membrane: bool = True

    # Numerical
    n_radial_nodes: int = 5
    n_axial_eval_points: int = 100


@dataclass
class SimulationResults:
    """Output result from 2D PDE solver."""

    co2_conversion_pct: float
    meoh_yield_pct: float
    h2o_removal_pct: float
    retentate_exit_p_h2o_bar: float
    carbon_balance_error: float
    is_catalyst_safe: bool
    status: str
    z_mesh: np.ndarray
    profiles_F: np.ndarray


class AnnularReactor2DSolver:
    """2D Heterogeneous Annular Membrane Reactor Solver."""

    def __init__(self, config: ReactorConfig):
        self.cfg = config
        self.r_m = 0.5 * self.cfg.d_membrane_m
        self.r_w = 0.5 * self.cfg.d_wall_m
        self.A_c = (np.pi / 4.0) * (self.cfg.d_wall_m**2 - self.cfg.d_membrane_m**2)
        self.a_m = (np.pi * self.cfg.d_membrane_m) / self.A_c
        self.V_bed_m3 = self.A_c * self.cfg.length_m

        # Molar feed flow at STP
        V_stp_s = (self.cfg.GHSV_h * self.V_bed_m3) / 3600.0
        self.F_tot_in = (V_stp_s * 1.01325e5) / (R_GAS * 273.15)

        # Inflow [CO2, H2, CH3OH, H2O, CO]
        self.F0 = np.array(
            [
                0.25 * self.F_tot_in,
                0.75 * self.F_tot_in,
                0.0,
                0.0,
                0.0,
            ]
        )

    def solve(self) -> SimulationResults:
        """Solves the axial-radial boundary value problem."""
        A_c = self.A_c
        a_m = self.a_m
        rho_bed = self.cfg.rho_bed_kg_m3
        P_ret = self.cfg.P_ret_Pa
        P_perm = self.cfg.P_perm_Pa
        T_op = self.cfg.T_op_K
        is_mem = self.cfg.is_membrane

        def ode_system(z: float, F: np.ndarray) -> np.ndarray:
            F_safe = np.maximum(F, 1e-12)
            F_tot = np.sum(F_safe)
            p_Pa = (F_safe / F_tot) * P_ret
            p_bar = p_Pa / 1.0e5

            # Catalytic rates (Mignard & Pritchard)
            r_meoh, r_rwgs, _ = calculate_mignard_pritchard_rates(p_bar, T_op)

            # Net generation [mol / (m^3 * s)]
            R_gen = rho_bed * np.array(
                [
                    -r_meoh - r_rwgs,  # CO2
                    -3.0 * r_meoh - r_rwgs,  # H2
                    r_meoh,  # CH3OH
                    r_meoh + r_rwgs,  # H2O
                    r_rwgs,  # CO
                ]
            )

            dFdz = A_c * R_gen

            if is_mem:
                # Map partial pressures to [H2O, CH3OH, H2]
                p_ret_ms = np.array([p_Pa[3], p_Pa[2], p_Pa[1]])
                p_perm_ms = np.array([0.05 * P_perm, 0.01 * P_perm, 0.02 * P_perm])

                J_ms = compute_maxwell_stefan_flux(p_ret_ms, p_perm_ms, T_K=T_op)

                # Sinks along membrane interface
                dFdz[3] -= a_m * A_c * J_ms[0]  # H2O
                dFdz[2] -= a_m * A_c * J_ms[1]  # CH3OH
                dFdz[1] -= a_m * A_c * J_ms[2]  # H2

            return dFdz

        sol = solve_ivp(
            ode_system,
            [0.0, self.cfg.length_m],
            self.F0,
            method="Radau",
            rtol=1e-7,
            atol=1e-9,
        )

        F_out = sol.y[:, -1]
        conv_CO2 = float((self.F0[0] - F_out[0]) / self.F0[0] * 100.0)
        yield_MeOH = float(F_out[2] / self.F0[0] * 100.0)

        total_h2o_gen = max(F_out[2] + F_out[4], 1e-9)
        rem_H2O = float(
            0.0 if not is_mem else (1.0 - (F_out[3] / total_h2o_gen)) * 100.0
        )

        p_final_bar = (F_out / np.sum(F_out)) * (P_ret / 1.0e5)
        p_h2o_exit_bar = float(p_final_bar[3])

        is_safe, _margin, safe_msg = check_catalyst_stability(
            p_h2o_exit_bar, P_ret / 1e5
        )

        # Carbon balance relative error
        n_c_in = self.F0[0]
        n_c_out = F_out[0] + F_out[2] + F_out[4]
        c_err = float(abs(n_c_in - n_c_out) / n_c_in)

        return SimulationResults(
            co2_conversion_pct=conv_CO2,
            meoh_yield_pct=yield_MeOH,
            h2o_removal_pct=rem_H2O,
            retentate_exit_p_h2o_bar=p_h2o_exit_bar,
            carbon_balance_error=c_err,
            is_catalyst_safe=is_safe,
            status=safe_msg,
            z_mesh=sol.t,
            profiles_F=sol.y,
        )
