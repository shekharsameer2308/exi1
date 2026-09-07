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
2D Heterogeneous Catalytic Membrane Reactor (CMR) Engine.
Solves the coupled (z, r) boundary value problem with radial dispersion,
desorption enthalpy sink, and exact elemental conservation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp

from core.kinetics import calculate_reaction_rates, check_catalyst_preservation
from core.thermodynamics import (
    MOLAR_MASSES,
    N_SPECIES,
    R_GAS,
    SPECIES_IDX,
    get_mixture_heat_capacity,
    get_reaction_enthalpies,
    peng_robinson_compressibility,
)
from core.transport_2d import (
    compute_effective_radial_conductivity,
    compute_radial_dispersion,
    compute_wall_heat_transfer_coefficient,
    update_dynamic_ergun,
)


@dataclass
class ReactorParameters:
    """Design and Operating Configuration for 2D Heterogeneous CMR."""

    # Geometry
    length_m: float = 6.0
    diameter_inner_m: float = 0.0254  # 1.0 inch ID
    d_p_m: float = 0.003  # 3 mm catalyst pellets
    bed_voidage: float = 0.40
    rho_b_kg_m3: float = 1150.0

    # Inflow
    T_in_K: float = 503.15  # 230 °C
    P_in_Pa: float = 50.0e5  # 50 bar
    GHSV_h: float = 6500.0  # h^-1 STP
    h2_co2_ratio: float = 3.0
    inert_fraction: float = 0.01  # 1.0% N2

    # Thermal Management
    T_cool_K: float = 503.15  # 230 °C
    U_wall_fixed: float | None = None

    # Membrane (Si-CHA)
    water_permeance_mol_m2_s_Pa: float = 2.5e-7  # at 230 °C
    permeance_Ea_kJ_mol: float = 12.0
    P_perm_Pa: float = 1.2e5  # 1.2 bar sweep / vacuum
    sweep_water_mol_fraction: float = 0.05
    dH_desorption_zeolite_kJ_mol: float = 45.0
    separation_factors: dict[str, float] = field(
        default_factory=lambda: {
            "H2O/H2": 220.0,
            "H2O/CO2": 450.0,
            "H2O/CH3OH": 600.0,
            "H2O/CO": 500.0,
            "H2O/N2": 500.0,
        }
    )

    # Discretization
    n_radial_nodes: int = 7  # Radial discretization points (r = 0 to R)
    n_axial_eval_points: int = 200


@dataclass
class Simulation2DResult:
    """Comprehensive 2D Simulation Result Object."""

    z_mesh: np.ndarray
    r_mesh: np.ndarray

    # Profiles: shape (n_z, n_r, n_species) or (n_z, n_r)
    C_profiles: np.ndarray  # Concentration [mol / m^3]
    T_profiles: np.ndarray  # Temperature [K]
    P_axial: np.ndarray  # Pressure [Pa]
    u_s_axial: np.ndarray  # Superficial velocity [m/s]

    # Fluxes and Rates
    r_meoh_grid: np.ndarray  # [mol / (kg_cat * s)]
    r_rwgs_grid: np.ndarray  # [mol / (kg_cat * s)]
    J_membrane: np.ndarray  # [mol / (m^2 * s)] for each species

    # Integrated Outlet Totals
    F_in_total_mol_s: float
    F_ret_out_total_mol_s: float
    F_perm_out_total_mol_s: float
    F_ret_out_species: np.ndarray  # shape (6,)
    F_perm_out_species: np.ndarray  # shape (6,)

    # Key Performance Indicators (KPIs)
    co2_conversion: float
    meoh_yield: float
    meoh_selectivity: float
    water_extraction_ratio: float
    min_axial_p_h2o_bar: float
    space_time_yield_kg_L_h: float
    recycle_ratio: float
    net_specific_compression_energy_kWh_kg: float
    max_radial_dT_K: float
    max_bed_temperature_K: float

    # Quality Control
    carbon_balance_error: float
    hydrogen_balance_error: float
    oxygen_balance_error: float
    is_catalyst_safe: bool
    status: str


class ReactorEngine2D:
    """
    2D Axisymmetric Heterogeneous Packed Bed Membrane Reactor Solver.
    """

    def __init__(self, params: ReactorParameters):
        self.p = params
        self.R_tube = 0.5 * self.p.diameter_inner_m
        self.A_c = np.pi * (self.R_tube**2)
        self.V_cat_m3 = self.A_c * self.p.length_m * (1.0 - self.p.bed_voidage)
        self.V_cat_L = self.V_cat_m3 * 1000.0

        # Radial discretization points using Chebyshev / equidistant Gauss-Lobatto
        self.Nr = self.p.n_radial_nodes
        # Equidistant radial grid for robust finite difference
        self.r_grid = np.linspace(0.0, self.R_tube, self.Nr)
        self.dr = self.R_tube / (self.Nr - 1)

        # Radial integration weights (trapezoidal in cylindrical coordinates 2*pi*r*dr / A_c)
        r_weights = np.zeros(self.Nr)
        for i in range(self.Nr):
            if i == 0:
                r_weights[i] = 0.5 * (self.r_grid[0] + 0.5 * self.dr) * 0.5 * self.dr
            elif i == self.Nr - 1:
                r_weights[i] = 0.5 * (self.r_grid[-1] - 0.5 * self.dr) * 0.5 * self.dr
            else:
                r_weights[i] = self.r_grid[i] * self.dr
        self.r_weights = (2.0 * np.pi * r_weights) / self.A_c
        self.r_weights /= np.sum(self.r_weights)  # Normalize

        # Calculate Feed Flow Rate from GHSV
        # GHSV = Volumetric STP Flow Rate / Volume of reactor bed
        V_bed_total_m3 = self.A_c * self.p.length_m
        V_stp_flow_m3_h = self.p.GHSV_h * V_bed_total_m3
        V_stp_flow_m3_s = V_stp_flow_m3_h / 3600.0
        # Molar flow at STP (T_stp = 273.15 K, P_stp = 1.01325e5 Pa)
        self.F_feed_total_mol_s = (V_stp_flow_m3_s * 1.01325e5) / (R_GAS * 273.15)

        # Feed Mole Fractions [CO2, H2, CO, CH3OH, H2O, N2]
        # H2/CO2 = ratio, inert_fraction = N2
        y_inert = self.p.inert_fraction
        y_reactive = 1.0 - y_inert
        y_co2 = y_reactive / (1.0 + self.p.h2_co2_ratio)
        y_h2 = self.p.h2_co2_ratio * y_co2

        self.y_in = np.array(
            [
                y_co2,  # CO2
                y_h2,  # H2
                0.0,  # CO
                0.0,  # CH3OH
                0.0,  # H2O
                y_inert,  # N2
            ]
        )
        self.F_in_species = self.F_feed_total_mol_s * self.y_in

    def solve(self) -> Simulation2DResult:
        """
        Integrates the 2D PDE along the axial coordinate z in [0, L].
        State vector y_state at each z contains:
        - C_i(r_k) for i in 0..5, k in 0..Nr-1 (6 * Nr states)
        - T(r_k) for k in 0..Nr-1 (Nr states)
        - P (1 state)
        - Cumulative permeate molar flows F_perm_i (6 states)
        Total states = 7 * Nr + 7
        """
        Nr = self.Nr
        idx_C = lambda sp_i, r_k: sp_i * Nr + r_k
        idx_T = lambda r_k: 6 * Nr + r_k
        idx_P = 7 * Nr
        idx_Fperm = lambda sp_i: 7 * Nr + 1 + sp_i
        n_total_states = 7 * Nr + 7

        # Initial Conditions at z = 0
        y0 = np.zeros(n_total_states)

        # Initial superficial velocity and initial concentrations
        Z_in, _rho_in = peng_robinson_compressibility(
            self.y_in, self.p.T_in_K, self.p.P_in_Pa
        )
        u_s_in = (self.F_feed_total_mol_s * Z_in * R_GAS * self.p.T_in_K) / (
            self.p.P_in_Pa * self.A_c
        )
        C_in_species = (self.y_in * self.p.P_in_Pa) / (Z_in * R_GAS * self.p.T_in_K)

        for sp_i in range(N_SPECIES):
            for r_k in range(Nr):
                y0[idx_C(sp_i, r_k)] = C_in_species[sp_i]

        for r_k in range(Nr):
            y0[idx_T(r_k)] = self.p.T_in_K

        y0[idx_P] = self.p.P_in_Pa
        for sp_i in range(N_SPECIES):
            y0[idx_Fperm(sp_i)] = 0.0

        def ode_rhs(z: float, state: np.ndarray) -> np.ndarray:
            dstate = np.zeros_like(state)
            P_loc = max(state[idx_P], 1.0e5)

            # Reconstruct profiles across radial nodes
            C_grid = np.zeros((N_SPECIES, Nr))
            for sp_i in range(N_SPECIES):
                for r_k in range(Nr):
                    C_grid[sp_i, r_k] = max(state[idx_C(sp_i, r_k)], 0.0)

            T_grid = np.zeros(Nr)
            for r_k in range(Nr):
                T_grid[r_k] = max(state[idx_T(r_k)], 200.0)

            # Compute cross-section averaged properties
            C_tot_r = np.sum(C_grid, axis=0)
            y_grid = C_grid / np.maximum(C_tot_r[np.newaxis, :], 1e-8)
            y_avg = np.dot(y_grid, self.r_weights)
            T_avg = np.dot(T_grid, self.r_weights)

            # Update Ergun velocity and pressure gradient
            np.sum(
                np.dot(C_grid, self.r_weights)
            ) * u_s_in * self.A_c  # approximate scale
            u_s, rho_g, dP_dz = update_dynamic_ergun(
                F_ret_total=self.F_feed_total_mol_s,
                y_ret=y_avg,
                T_K=T_avg,
                P_Pa=P_loc,
                A_c=self.A_c,
                d_p=self.p.d_p_m,
                eps=self.p.bed_voidage,
            )
            dstate[idx_P] = dP_dz

            # Effective transport coefficients
            D_er = compute_radial_dispersion(u_s, self.p.d_p_m, eps=self.p.bed_voidage)
            Cp_mix = get_mixture_heat_capacity(y_avg, T_avg)
            k_er = compute_effective_radial_conductivity(
                u_s=u_s,
                rho_g=rho_g,
                Cp_g=Cp_mix,
                d_p=self.p.d_p_m,
                eps=self.p.bed_voidage,
            )
            U_wall = (
                self.p.U_wall_fixed
                if self.p.U_wall_fixed is not None
                else compute_wall_heat_transfer_coefficient(
                    u_s=u_s,
                    rho_g=rho_g,
                    mu_g=1.5e-5,
                    Cp_g=Cp_mix,
                    k_g=0.04,
                    d_p=self.p.d_p_m,
                    d_t=self.p.diameter_inner_m,
                )
            )

            # Local reaction rates at each radial node
            dH1, dH2 = get_reaction_enthalpies(T_avg)

            # Membrane water permeance at local wall temperature
            T_wall = T_grid[-1]
            Q_h2o_T = self.p.water_permeance_mol_m2_s_Pa * np.exp(
                -(self.p.permeance_Ea_kJ_mol * 1e3 / R_GAS)
                * (1.0 / T_wall - 1.0 / 503.15)
            )

            # Wall partial pressures [bar]
            p_wall_bar = y_grid[:, -1] * (P_loc / 1e5)
            p_perm_water_bar = (
                self.p.P_perm_Pa / 1e5
            ) * self.p.sweep_water_mol_fraction

            # Membrane Fluxes J_i [mol / (m^2 * s)]
            # Water flux
            driving_force_water_Pa = max(
                (p_wall_bar[SPECIES_IDX["H2O"]] - p_perm_water_bar) * 1e5, 0.0
            )
            J_water = Q_h2o_T * driving_force_water_Pa

            # Minor component leaks via separation factors
            J_fluxes = np.zeros(N_SPECIES)
            J_fluxes[SPECIES_IDX["H2O"]] = J_water
            J_fluxes[SPECIES_IDX["H2"]] = J_water / self.p.separation_factors["H2O/H2"]
            J_fluxes[SPECIES_IDX["CO2"]] = (
                J_water / self.p.separation_factors["H2O/CO2"]
            )
            J_fluxes[SPECIES_IDX["CH3OH"]] = (
                J_water / self.p.separation_factors["H2O/CH3OH"]
            )
            J_fluxes[SPECIES_IDX["CO"]] = J_water / self.p.separation_factors["H2O/CO"]
            J_fluxes[SPECIES_IDX["N2"]] = J_water / self.p.separation_factors["H2O/N2"]

            # Record cumulative permeate derivatives: dF_perm_i / dz = pi * d_t * J_i
            d_m = self.p.diameter_inner_m
            for sp_i in range(N_SPECIES):
                dstate[idx_Fperm(sp_i)] = np.pi * d_m * J_fluxes[sp_i]

            # Thermal desorption energy sink from zeolite lattice
            # q_sink = pi * d_m * J_water * [ dH_des_zeo + Cp_water * (T_wall - T_perm) ]
            dH_des_J_mol = self.p.dH_desorption_zeolite_kJ_mol * 1e3
            q_desorption_sink = (
                np.pi * d_m * J_water * (dH_des_J_mol + 35.0 * (T_wall - 483.15))
            )

            # Solve Radial Finite Difference for each species and temperature
            dr = self.dr
            dr2 = dr**2

            for r_k in range(Nr):
                r_val = self.r_grid[r_k]
                p_r_bar = y_grid[:, r_k] * (P_loc / 1e5)
                T_k = T_grid[r_k]

                r_meoh, r_rwgs, _ = calculate_reaction_rates(p_r_bar, T_k)

                # Net generation rates R_i [mol / (m^3_bed * s)] = rho_b * sum(nu_ij * r_j)
                rho_b = self.p.rho_b_kg_m3
                R_gen = np.array(
                    [
                        rho_b * (-r_meoh - r_rwgs),  # CO2
                        rho_b * (-3.0 * r_meoh - r_rwgs),  # H2
                        rho_b * (r_rwgs),  # CO
                        rho_b * (r_meoh),  # CH3OH
                        rho_b * (r_meoh + r_rwgs),  # H2O
                        0.0,  # N2
                    ]
                )

                # Reaction heat release Q_rxn [W / m^3_bed]
                Q_rxn = rho_b * ((-dH1) * r_meoh + (-dH2) * r_rwgs)

                # Spatial Radial Laplacian d^2/dr^2 + (1/r) d/dr
                if r_k == 0:
                    # Symmetry boundary at centerline r = 0: lim_{r->0} (1/r) dC/dr = d^2C/dr^2
                    # Laplacian = 2 * (C[1] - C[0]) / dr^2
                    for sp_i in range(N_SPECIES):
                        lap_C = 2.0 * (C_grid[sp_i, 1] - C_grid[sp_i, 0]) / dr2
                        dstate[idx_C(sp_i, r_k)] = (D_er * lap_C + R_gen[sp_i]) / u_s

                    lap_T = 2.0 * (T_grid[1] - T_grid[0]) / dr2
                    dstate[idx_T(r_k)] = (k_er * lap_T + Q_rxn) / (rho_g * Cp_mix * u_s)

                elif r_k == Nr - 1:
                    # Wall Boundary at r = R_tube:
                    # Mass: - D_er * (dC/dr)_wall = J_membrane_flux
                    # Heat: - k_er * (dT/dr)_wall = U_wall * (T_wall - T_cool) + (q_desorption / (pi * d_m))
                    # Ghost node approximation: C_ghost = C[Nr-2] - 2*dr*(J / D_er)
                    for sp_i in range(N_SPECIES):
                        dC_dr_wall = -J_fluxes[sp_i] / max(D_er, 1e-8)
                        C_ghost = C_grid[sp_i, Nr - 2] + 2.0 * dr * dC_dr_wall
                        lap_C = (
                            C_ghost - 2.0 * C_grid[sp_i, Nr - 1] + C_grid[sp_i, Nr - 2]
                        ) / dr2 + (1.0 / r_val) * dC_dr_wall
                        dstate[idx_C(sp_i, r_k)] = (D_er * lap_C + R_gen[sp_i]) / u_s

                    # Wall thermal flux including external cooling and endothermic desorption sink
                    q_wall_total = U_wall * (T_wall - self.p.T_cool_K) + (
                        q_desorption_sink / (np.pi * d_m)
                    )
                    dT_dr_wall = -q_wall_total / max(k_er, 1e-4)
                    T_ghost = T_grid[Nr - 2] + 2.0 * dr * dT_dr_wall
                    lap_T = (T_ghost - 2.0 * T_grid[Nr - 1] + T_grid[Nr - 2]) / dr2 + (
                        1.0 / r_val
                    ) * dT_dr_wall
                    dstate[idx_T(r_k)] = (k_er * lap_T + Q_rxn) / (rho_g * Cp_mix * u_s)

                else:
                    # Interior radial nodes
                    for sp_i in range(N_SPECIES):
                        d2C = (
                            C_grid[sp_i, r_k + 1]
                            - 2.0 * C_grid[sp_i, r_k]
                            + C_grid[sp_i, r_k - 1]
                        ) / dr2
                        dC_dr = (C_grid[sp_i, r_k + 1] - C_grid[sp_i, r_k - 1]) / (
                            2.0 * dr
                        )
                        lap_C = d2C + (1.0 / r_val) * dC_dr
                        dstate[idx_C(sp_i, r_k)] = (D_er * lap_C + R_gen[sp_i]) / u_s

                    d2T = (T_grid[r_k + 1] - 2.0 * T_grid[r_k] + T_grid[r_k - 1]) / dr2
                    dT_dr = (T_grid[r_k + 1] - T_grid[r_k - 1]) / (2.0 * dr)
                    lap_T = d2T + (1.0 / r_val) * dT_dr
                    dstate[idx_T(r_k)] = (k_er * lap_T + Q_rxn) / (rho_g * Cp_mix * u_s)

            return dstate

        # Solve ODE system along reactor length
        z_span = (0.0, self.p.length_m)
        z_eval = np.linspace(0.0, self.p.length_m, self.p.n_axial_eval_points)

        sol = solve_ivp(
            fun=ode_rhs,
            t_span=z_span,
            y0=y0,
            t_eval=z_eval,
            method="Radau",  # Implicit stiff solver
            rtol=1e-5,
            atol=1e-7,
        )

        # Post-process results
        z_mesh = sol.t
        n_z = len(z_mesh)

        C_profiles = np.zeros((n_z, Nr, N_SPECIES))
        T_profiles = np.zeros((n_z, Nr))
        P_axial = sol.y[idx_P, :]

        for sp_i in range(N_SPECIES):
            for r_k in range(Nr):
                C_profiles[:, r_k, sp_i] = sol.y[idx_C(sp_i, r_k), :]

        for r_k in range(Nr):
            T_profiles[:, r_k] = sol.y[idx_T(r_k), :]

        # Reconstruct velocities and integrated molar flow rates at outlet
        u_s_axial = np.zeros(n_z)
        r_meoh_grid = np.zeros((n_z, Nr))
        r_rwgs_grid = np.zeros((n_z, Nr))
        J_membrane = np.zeros((n_z, N_SPECIES))

        for iz in range(n_z):
            C_tot_r = np.sum(C_profiles[iz, :, :], axis=1)
            y_loc = C_profiles[iz, :, :] / np.maximum(C_tot_r[:, np.newaxis], 1e-8)
            y_avg = np.dot(y_loc.T, self.r_weights)
            T_avg = np.dot(T_profiles[iz, :], self.r_weights)

            u_s, _, _ = update_dynamic_ergun(
                F_ret_total=self.F_feed_total_mol_s,
                y_ret=y_avg,
                T_K=T_avg,
                P_Pa=P_axial[iz],
                A_c=self.A_c,
                d_p=self.p.d_p_m,
                eps=self.p.bed_voidage,
            )
            u_s_axial[iz] = u_s

            for r_k in range(Nr):
                r_m, r_w, _ = calculate_reaction_rates(
                    y_loc[r_k, :] * (P_axial[iz] / 1e5), T_profiles[iz, r_k]
                )
                r_meoh_grid[iz, r_k] = r_m
                r_rwgs_grid[iz, r_k] = r_w

            # Wall water flux
            T_w = T_profiles[iz, -1]
            Q_w = self.p.water_permeance_mol_m2_s_Pa * np.exp(
                -(self.p.permeance_Ea_kJ_mol * 1e3 / R_GAS) * (1.0 / T_w - 1.0 / 503.15)
            )
            p_w_h2o = y_loc[-1, SPECIES_IDX["H2O"]] * (P_axial[iz] / 1e5)
            p_perm_h2o = (self.p.P_perm_Pa / 1e5) * self.p.sweep_water_mol_fraction
            J_membrane[iz, SPECIES_IDX["H2O"]] = Q_w * max(
                (p_w_h2o - p_perm_h2o) * 1e5, 0.0
            )

        # Outlet retentate molar flows [mol / s] = integral(2*pi*r * u_s * C_i dr)
        u_s_out = u_s_axial[-1]
        F_ret_out_species = np.zeros(N_SPECIES)
        for sp_i in range(N_SPECIES):
            C_out_radial = C_profiles[-1, :, sp_i]
            # Average concentration
            C_out_avg = np.dot(C_out_radial, self.r_weights)
            F_ret_out_species[sp_i] = C_out_avg * u_s_out * self.A_c

        # Cumulative permeate outlet molar flows [mol / s]
        F_perm_out_species = np.array(
            [sol.y[idx_Fperm(sp_i), -1] for sp_i in range(N_SPECIES)]
        )

        # Total molar flows
        F_in_total = self.F_feed_total_mol_s
        F_ret_out_total = np.sum(F_ret_out_species)
        F_perm_out_total = np.sum(F_perm_out_species)

        # Performance Indicators
        F_co2_in = self.F_in_species[SPECIES_IDX["CO2"]]
        F_co2_out_ret = F_ret_out_species[SPECIES_IDX["CO2"]]
        F_co2_out_perm = F_perm_out_species[SPECIES_IDX["CO2"]]

        co2_conversion = (F_co2_in - (F_co2_out_ret + F_co2_out_perm)) / F_co2_in
        meoh_yield = (
            F_ret_out_species[SPECIES_IDX["CH3OH"]]
            + F_perm_out_species[SPECIES_IDX["CH3OH"]]
        ) / F_co2_in
        meoh_selectivity = meoh_yield / max(co2_conversion, 1e-8)

        # Water extraction ratio = Permeated H2O / Total Formed H2O
        # Formed H2O = Retentate H2O + Permeated H2O
        total_h2o_produced = (
            F_ret_out_species[SPECIES_IDX["H2O"]]
            + F_perm_out_species[SPECIES_IDX["H2O"]]
        )
        water_extraction_ratio = F_perm_out_species[SPECIES_IDX["H2O"]] / max(
            total_h2o_produced, 1e-8
        )

        # Minimum Axial Water Partial Pressure in retentate bed
        p_h2o_axial_bar = np.zeros(n_z)
        for iz in range(n_z):
            C_tot_r = np.sum(C_profiles[iz, :, :], axis=1)
            y_loc = C_profiles[iz, :, :] / np.maximum(C_tot_r[:, np.newaxis], 1e-8)
            y_avg = np.dot(y_loc.T, self.r_weights)
            p_h2o_axial_bar[iz] = y_avg[SPECIES_IDX["H2O"]] * (P_axial[iz] / 1e5)

        min_p_h2o_bar = float(
            np.min(p_h2o_axial_bar[1:])
        )  # Exclude exact inlet point where no reaction occurred yet

        # Space-Time Yield [kg_MeOH / (L_cat * h)]
        meoh_rate_kg_s = (
            F_ret_out_species[SPECIES_IDX["CH3OH"]]
            + F_perm_out_species[SPECIES_IDX["CH3OH"]]
        ) * MOLAR_MASSES[SPECIES_IDX["CH3OH"]]
        meoh_rate_kg_h = meoh_rate_kg_s * 3600.0
        space_time_yield = meoh_rate_kg_h / self.V_cat_L

        # Recycle Ratio: R = F_unreacted_recycle / F_fresh_feed
        # Unreacted (H2 + CO2 + CO) in retentate
        F_unreacted_ret = (
            F_ret_out_species[SPECIES_IDX["CO2"]]
            + F_ret_out_species[SPECIES_IDX["H2"]]
            + F_ret_out_species[SPECIES_IDX["CO"]]
        )
        recycle_ratio = F_unreacted_ret / F_in_total

        # Net Specific Energy Consumption [kWh / kg_MeOH]
        # Includes main feed compression + recycle loop compression + permeate auxiliary vacuum pump work
        # Work = (gamma / (gamma - 1)) * R * T_in * [ (P_out/P_in)^((gamma-1)/gamma) - 1 ] / eta
        # Main feed compression from 30 bar green H2/CO2 to 50 bar
        W_feed_comp_kJ_mol = (
            (1.4 / 0.4)
            * R_GAS
            * 300.0
            * (((50.0 / 30.0) ** (0.4 / 1.4)) - 1.0)
            / (0.78 * 1000.0)
        )
        # Recycle compression (dP ~ 2.5 bar)
        W_rec_comp_kJ_mol = (
            (1.4 / 0.4)
            * R_GAS
            * 310.0
            * (((50.0 / 47.5) ** (0.4 / 1.4)) - 1.0)
            / (0.78 * 1000.0)
        )
        # Permeate vacuum pump / recompression (from 1.2 bar to 1.0 bar / condenser)
        W_perm_pump_kJ_mol = (
            (1.33 / 0.33)
            * R_GAS
            * 350.0
            * (((1.2 / 1.0) ** (0.33 / 1.33)) - 1.0)
            / (0.75 * 1000.0)
        )

        P_feed_kW = F_in_total * W_feed_comp_kJ_mol
        P_rec_kW = F_unreacted_ret * W_rec_comp_kJ_mol
        P_perm_kW = F_perm_out_total * W_perm_pump_kJ_mol
        Total_Power_kW = P_feed_kW + P_rec_kW + P_perm_kW

        specific_energy_kWh_kg = Total_Power_kW / max(meoh_rate_kg_h, 1e-4)

        # Thermal Metrics
        max_T_bed = float(np.max(T_profiles))
        radial_dT_axial = np.max(T_profiles, axis=1) - np.min(T_profiles, axis=1)
        max_radial_dT = float(np.max(radial_dT_axial))

        # Atomic Conservation Checks
        # Carbon Balance: CO2 + CO + CH3OH
        n_C_in = self.F_in_species[0] + self.F_in_species[2] + self.F_in_species[3]
        n_C_out = (
            F_ret_out_species[0]
            + F_ret_out_species[2]
            + F_ret_out_species[3]
            + F_perm_out_species[0]
            + F_perm_out_species[2]
            + F_perm_out_species[3]
        )
        c_err = abs(n_C_in - n_C_out) / max(n_C_in, 1e-8)

        # Hydrogen Balance: 2*H2 + 4*CH3OH + 2*H2O
        n_H_in = (
            2.0 * self.F_in_species[1]
            + 4.0 * self.F_in_species[3]
            + 2.0 * self.F_in_species[4]
        )
        n_H_out = (
            2.0 * F_ret_out_species[1]
            + 4.0 * F_ret_out_species[3]
            + 2.0 * F_ret_out_species[4]
            + 2.0 * F_perm_out_species[1]
            + 4.0 * F_perm_out_species[3]
            + 2.0 * F_perm_out_species[4]
        )
        h_err = abs(n_H_in - n_H_out) / max(n_H_in, 1e-8)

        # Oxygen Balance: 2*CO2 + CO + CH3OH + H2O
        n_O_in = (
            2.0 * self.F_in_species[0]
            + self.F_in_species[2]
            + self.F_in_species[3]
            + self.F_in_species[4]
        )
        n_O_out = (
            2.0 * F_ret_out_species[0]
            + F_ret_out_species[2]
            + F_ret_out_species[3]
            + F_ret_out_species[4]
            + 2.0 * F_perm_out_species[0]
            + F_perm_out_species[2]
            + F_perm_out_species[3]
            + F_perm_out_species[4]
        )
        o_err = abs(n_O_in - n_O_out) / max(n_O_in, 1e-8)

        # Safety Evaluation
        is_safe, _margin, safe_msg = check_catalyst_preservation(
            min_p_h2o_bar, self.p.P_in_Pa / 1e5
        )

        return Simulation2DResult(
            z_mesh=z_mesh,
            r_mesh=self.r_grid,
            C_profiles=C_profiles,
            T_profiles=T_profiles,
            P_axial=P_axial,
            u_s_axial=u_s_axial,
            r_meoh_grid=r_meoh_grid,
            r_rwgs_grid=r_rwgs_grid,
            J_membrane=J_membrane,
            F_in_total_mol_s=F_in_total,
            F_ret_out_total_mol_s=F_ret_out_total,
            F_perm_out_total_mol_s=F_perm_out_total,
            F_ret_out_species=F_ret_out_species,
            F_perm_out_species=F_perm_out_species,
            co2_conversion=co2_conversion,
            meoh_yield=meoh_yield,
            meoh_selectivity=meoh_selectivity,
            water_extraction_ratio=water_extraction_ratio,
            min_axial_p_h2o_bar=min_p_h2o_bar,
            space_time_yield_kg_L_h=space_time_yield,
            recycle_ratio=recycle_ratio,
            net_specific_compression_energy_kWh_kg=specific_energy_kWh_kg,
            max_radial_dT_K=max_radial_dT,
            max_bed_temperature_K=max_T_bed,
            carbon_balance_error=c_err,
            hydrogen_balance_error=h_err,
            oxygen_balance_error=o_err,
            is_catalyst_safe=is_safe,
            status=f"{sol.message} | Catalyst: {safe_msg}",
        )
