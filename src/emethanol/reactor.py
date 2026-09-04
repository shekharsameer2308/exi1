"""
1D Plug Flow Membrane Reactor for E-Methanol Synthesis.
Modular, non-isothermal, stiff ODE physics engine.
"""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass, field

from src.emethanol.properties import R_GAS
from src.emethanol.thermodynamics import STOICHIOMETRIC_MATRIX
from src.emethanol.kinetics import calculate_rates
from src.emethanol.membrane import calculate_membrane_flux
from src.emethanol.balances import evaluate_derivatives
from src.emethanol.validation import compute_elemental_balances, validate_simulation_physics


class ODENonConvergenceError(Exception):
    """Custom exception raised when the ODE solver fails to converge."""
    pass


@dataclass
class ModelConfig:
    """Versioned configuration for reactor physics engine."""
    kinetic_model: str = "VBF"                # "VBF" or "MIGNARD_PRITCHARD"
    membrane_model: str = "LDF"               # "LDF" or "MAXWELL_STEFAN"
    membrane_enabled: bool = True             # True: MR mode, False: TR mode
    non_isothermal: bool = True               # True: solve dT/dz, False: isothermal
    pressure_drop: bool = False               # True: solve Ergun dP/dz, False: isobaric
    water_permeance: float = 1.0e-7           # mol / (m^2 * s * Pa)
    membrane_activation_energy: float = 0.0   # J/mol
    overall_heat_transfer_coeff: float = 50.0 # W / (m^2 * K)
    particle_diameter: float = 0.002          # m (2 mm catalyst pellets)
    solver_method: str = "BDF"                # "BDF", "Radau", or "LSODA"
    rtol: float = 1e-6
    atol: float = 1e-9


@dataclass
class ReactorSimulationResult:
    """Structured container for reactor simulation performance and axial profiles."""
    # Summary scalar outputs
    co2_conversion: float = 0.0
    meoh_yield: float = 0.0
    meoh_selectivity: float = 0.0
    h2o_removal_fraction: float = 0.0
    h2_loss_fraction: float = 0.0
    co_formation_fraction: float = 0.0
    outlet_temperature: float = 0.0
    max_temperature: float = 0.0
    outlet_pressure: float = 0.0
    pressure_drop_bar: float = 0.0
    residence_time_sec: float = 0.0
    
    # Solver diagnostics & Conservation
    solver_success: bool = False
    solver_message: str = ""
    carbon_balance_error: float = 0.0
    hydrogen_balance_error: float = 0.0
    oxygen_balance_error: float = 0.0
    is_physically_valid: bool = False
    validation_message: str = ""
    
    # Axial profiles [z_grid]
    z_grid: np.ndarray = field(default_factory=lambda: np.array([]))
    F_CO2: np.ndarray = field(default_factory=lambda: np.array([]))
    F_H2: np.ndarray = field(default_factory=lambda: np.array([]))
    F_CO: np.ndarray = field(default_factory=lambda: np.array([]))
    F_CH3OH: np.ndarray = field(default_factory=lambda: np.array([]))
    F_H2O: np.ndarray = field(default_factory=lambda: np.array([]))
    y_CO2: np.ndarray = field(default_factory=lambda: np.array([]))
    y_H2: np.ndarray = field(default_factory=lambda: np.array([]))
    y_CO: np.ndarray = field(default_factory=lambda: np.array([]))
    y_CH3OH: np.ndarray = field(default_factory=lambda: np.array([]))
    y_H2O: np.ndarray = field(default_factory=lambda: np.array([]))
    T_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    P_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    r_meoh_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    r_rwgs_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    j_h2o_flux_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    cumulative_h2o_removed: np.ndarray = field(default_factory=lambda: np.array([]))

    def to_dict(self) -> Dict[str, Any]:
        """Convert scalar summary outputs to a dictionary."""
        return {
            "co2_conversion": self.co2_conversion,
            "meoh_yield": self.meoh_yield,
            "meoh_selectivity": self.meoh_selectivity,
            "h2o_removal_fraction": self.h2o_removal_fraction,
            "h2_loss_fraction": self.h2_loss_fraction,
            "co_formation_fraction": self.co_formation_fraction,
            "outlet_temperature": self.outlet_temperature,
            "max_temperature": self.max_temperature,
            "outlet_pressure": self.outlet_pressure,
            "pressure_drop_bar": self.pressure_drop_bar,
            "carbon_balance_error": self.carbon_balance_error,
            "hydrogen_balance_error": self.hydrogen_balance_error,
            "oxygen_balance_error": self.oxygen_balance_error,
            "solver_success": self.solver_success,
            "solver_message": self.solver_message,
            "is_physically_valid": self.is_physically_valid,
            "validation_message": self.validation_message,
        }


class MembraneReactor1D:
    """
    1D Plug Flow Membrane Reactor model.
    Implements full modular CRE physics, thermal balances, and conservation checks.
    """

    def __init__(
        self,
        length: float = 1.0,
        diameter: float = 0.02,
        rho_cat: float = 1100.0,
        void_frac: float = 0.4,
        config: Optional[ModelConfig] = None,
    ):
        if length <= 0 or diameter <= 0 or rho_cat <= 0:
            raise ValueError("Reactor geometry and catalyst density must be strictly positive.")
        if not (0 < void_frac < 1):
            raise ValueError("Void fraction must be between 0 and 1 exclusive.")

        self.L = float(length)
        self.D = float(diameter)
        self.A_cs = np.pi * (self.D ** 2) / 4.0
        self.V_rxn = self.A_cs * self.L
        self.A_mem = np.pi * self.D * self.L
        self.rho_cat = float(rho_cat)
        self.eps = float(void_frac)
        self.cat_mass = self.rho_cat * self.V_rxn
        self.config = config or ModelConfig()

    def simulate(
        self,
        T_in: float,
        P_in: float,
        flow_in: float,
        h2_co2_ratio: float,
        water_permeance: Optional[float] = None,
        sweep_flow: float = 0.0,
        coolant_temp: Optional[float] = None,
        config: Optional[ModelConfig] = None,
        n_points: int = 100,
    ) -> Dict[str, Any]:
        """
        Backwards-compatible simulation method returning dictionary of performance metrics.
        """
        cfg = config or self.config
        if water_permeance is not None:
            cfg.water_permeance = water_permeance

        res = self.solve(
            T_in=T_in,
            P_in=P_in,
            flow_in=flow_in,
            h2_co2_ratio=h2_co2_ratio,
            sweep_flow=sweep_flow,
            coolant_temp=coolant_temp,
            config=cfg,
            n_points=n_points,
        )

        if not res.solver_success:
            raise ODENonConvergenceError(f"ODE Solver failed: {res.solver_message}")

        return res.to_dict()

    def solve(
        self,
        T_in: float,
        P_in: float,
        flow_in: float,
        h2_co2_ratio: float,
        sweep_flow: float = 0.0,
        coolant_temp: Optional[float] = None,
        config: Optional[ModelConfig] = None,
        n_points: int = 100,
    ) -> ReactorSimulationResult:
        """
        Solves the differential ODE equations and returns complete ReactorSimulationResult.
        """
        cfg = config or self.config
        T_cool = coolant_temp if coolant_temp is not None else T_in

        if flow_in <= 0 or P_in <= 0 or h2_co2_ratio <= 0 or T_in <= 0:
            return ReactorSimulationResult(
                solver_success=False,
                solver_message="Invalid non-positive input conditions.",
                is_physically_valid=False,
                validation_message="Input domain error",
            )

        # Inlet molar flows [mol/s]: [CO2, H2, CO, MeOH, H2O]
        F_CO2_0 = flow_in / (1.0 + h2_co2_ratio)
        F_H2_0 = flow_in - F_CO2_0
        F0 = np.array([F_CO2_0, F_H2_0, 0.0, 0.0, 0.0])

        # Initial state vector (12 states):
        # [F_CO2, F_H2, F_CO, F_MeOH, F_H2O, T, P, F_CO2_p, F_H2_p, F_CO_p, F_MeOH_p, F_H2O_p]
        state_0 = np.array([
            F_CO2_0, F_H2_0, 0.0, 0.0, 0.0,
            T_in, P_in,
            0.0, 0.0, 0.0, 0.0, 0.0
        ])

        sweep_pp = np.zeros(5)

        def rhs(z: float, state: np.ndarray) -> np.ndarray:
            return evaluate_derivatives(
                z=z,
                state=state,
                reactor_diameter=self.D,
                catalyst_density=self.rho_cat,
                void_fraction=self.eps,
                particle_diameter=cfg.particle_diameter,
                overall_heat_transfer_coeff=cfg.overall_heat_transfer_coeff,
                coolant_temperature=T_cool,
                sweep_partial_pressures=sweep_pp,
                kinetic_model=cfg.kinetic_model,
                membrane_model=cfg.membrane_model,
                membrane_enabled=cfg.membrane_enabled,
                water_permeance=cfg.water_permeance,
                membrane_activation_energy=cfg.membrane_activation_energy,
                non_isothermal=cfg.non_isothermal,
                pressure_drop=cfg.pressure_drop,
            )

        z_eval = np.linspace(0, self.L, n_points)
        try:
            sol = solve_ivp(
                rhs,
                [0, self.L],
                state_0,
                method=cfg.solver_method,
                t_eval=z_eval,
                rtol=cfg.rtol,
                atol=cfg.atol,
            )
        except Exception as e:
            return ReactorSimulationResult(
                solver_success=False,
                solver_message=f"ODE solver exception: {str(e)}",
                is_physically_valid=False,
                validation_message="Integration exception",
            )

        if not sol.success:
            return ReactorSimulationResult(
                solver_success=False,
                solver_message=sol.message,
                is_physically_valid=False,
                validation_message="ODE solver non-convergence",
            )

        # Extract solution trajectories
        z_grid = sol.t
        states = sol.y  # shape: (12, n_points)
        F_CO2 = np.maximum(states[0, :], 0.0)
        F_H2 = np.maximum(states[1, :], 0.0)
        F_CO = np.maximum(states[2, :], 0.0)
        F_CH3OH = np.maximum(states[3, :], 0.0)
        F_H2O = np.maximum(states[4, :], 0.0)
        T_prof = states[5, :]
        P_prof = states[6, :]
        
        # Cumulative permeated species flows
        F_perm_prof = np.maximum(states[7:12, :], 0.0)
        cum_h2o_removed = F_perm_prof[4, :]
        total_permeated = F_perm_prof[:, -1]

        F_tot_prof = F_CO2 + F_H2 + F_CO + F_CH3OH + F_H2O
        y_CO2 = F_CO2 / F_tot_prof
        y_H2 = F_H2 / F_tot_prof
        y_CO = F_CO / F_tot_prof
        y_CH3OH = F_CH3OH / F_tot_prof
        y_H2O = F_H2O / F_tot_prof

        # Calculate rate and flux profiles along z
        n_pts = len(z_grid)
        r_meoh_prof = np.zeros(n_pts)
        r_rwgs_prof = np.zeros(n_pts)
        j_h2o_prof = np.zeros(n_pts)

        for k in range(n_pts):
            p_k = np.array([y_CO2[k], y_H2[k], y_CO[k], y_CH3OH[k], y_H2O[k]]) * P_prof[k]
            rm, rr = calculate_rates(p_k, T_prof[k], model=cfg.kinetic_model)
            r_meoh_prof[k] = rm
            r_rwgs_prof[k] = rr

            if cfg.membrane_enabled:
                flux_k = calculate_membrane_flux(
                    partial_pressures_rxn=p_k,
                    partial_pressures_sweep=sweep_pp,
                    T_K=T_prof[k],
                    model=cfg.membrane_model,
                    permeance_h2o_base=cfg.water_permeance,
                    activation_energy_h2o=cfg.membrane_activation_energy,
                )
                j_h2o_prof[k] = flux_k[4]

        # Outlet values
        F_out = np.array([F_CO2[-1], F_H2[-1], F_CO[-1], F_CH3OH[-1], F_H2O[-1]])
        co2_conv = (F0[0] - F_out[0] - total_permeated[0]) / F0[0]
        meoh_yield = (F_out[3] + total_permeated[3]) / F0[0]
        co_formed = (F_out[2] + total_permeated[2]) / F0[0]
        
        total_c_products = (F_out[3] + total_permeated[3]) + (F_out[2] + total_permeated[2])
        meoh_sel = ((F_out[3] + total_permeated[3]) / total_c_products) if total_c_products > 1e-10 else 0.0
        
        total_h2o_gen = (F_out[3] + total_permeated[3]) + (F_out[2] + total_permeated[2])
        h2o_removal_frac = (total_permeated[4] / total_h2o_gen) if total_h2o_gen > 1e-10 else 0.0
        h2_loss_frac = (total_permeated[1] / F0[1]) if F0[1] > 1e-10 else 0.0

        # Elemental balances
        elem_errs = compute_elemental_balances(F0, F_out, total_permeated)

        res = ReactorSimulationResult(
            co2_conversion=float(co2_conv),
            meoh_yield=float(meoh_yield),
            meoh_selectivity=float(meoh_sel),
            h2o_removal_fraction=float(h2o_removal_frac),
            h2_loss_fraction=float(h2_loss_frac),
            co_formation_fraction=float(co_formed),
            outlet_temperature=float(T_prof[-1]),
            max_temperature=float(np.max(T_prof)),
            outlet_pressure=float(P_prof[-1]),
            pressure_drop_bar=float(P_in - P_prof[-1]),
            solver_success=True,
            solver_message="Convergence achieved",
            carbon_balance_error=elem_errs["carbon_balance_error"],
            hydrogen_balance_error=elem_errs["hydrogen_balance_error"],
            oxygen_balance_error=elem_errs["oxygen_balance_error"],
            z_grid=z_grid,
            F_CO2=F_CO2,
            F_H2=F_H2,
            F_CO=F_CO,
            F_CH3OH=F_CH3OH,
            F_H2O=F_H2O,
            y_CO2=y_CO2,
            y_H2=y_H2,
            y_CO=y_CO,
            y_CH3OH=y_CH3OH,
            y_H2O=y_H2O,
            T_profile=T_prof,
            P_profile=P_prof,
            r_meoh_profile=r_meoh_prof,
            r_rwgs_profile=r_rwgs_prof,
            j_h2o_flux_profile=j_h2o_prof,
            cumulative_h2o_removed=cum_h2o_removed,
        )

        is_valid, msg = validate_simulation_physics(res.to_dict())
        res.is_physically_valid = is_valid
        res.validation_message = msg

        return res


def simulate_reactor(
    temperature: float = 493.15,
    pressure: float = 50.0,
    co2_flow: Optional[float] = None,
    h2_flow: Optional[float] = None,
    total_flow: float = 0.015,
    h2_co2_ratio: float = 3.0,
    sweep_flow: float = 0.0,
    reactor_length: float = 1.0,
    reactor_diameter: float = 0.02,
    water_permeance: float = 1.0e-7,
    kinetic_model: str = "VBF",
    membrane_model: str = "LDF",
    membrane_enabled: bool = True,
    non_isothermal: bool = True,
    pressure_drop: bool = False,
    coolant_temperature: Optional[float] = None,
    overall_heat_transfer_coeff: float = 50.0,
    solver_method: str = "BDF",
    rtol: float = 1e-6,
    atol: float = 1e-9,
) -> ReactorSimulationResult:
    """
    High-level functional API to simulate 1D packed-bed membrane / conventional reactor.
    """
    if co2_flow is not None and h2_flow is not None:
        flow_in = co2_flow + h2_flow
        ratio = h2_flow / co2_flow if co2_flow > 0 else 3.0
    else:
        flow_in = total_flow
        ratio = h2_co2_ratio

    cfg = ModelConfig(
        kinetic_model=kinetic_model,
        membrane_model=membrane_model,
        membrane_enabled=membrane_enabled,
        non_isothermal=non_isothermal,
        pressure_drop=pressure_drop,
        water_permeance=water_permeance,
        overall_heat_transfer_coeff=overall_heat_transfer_coeff,
        solver_method=solver_method,
        rtol=rtol,
        atol=atol,
    )

    reactor = MembraneReactor1D(
        length=reactor_length,
        diameter=reactor_diameter,
        config=cfg,
    )

    return reactor.solve(
        T_in=temperature,
        P_in=pressure,
        flow_in=flow_in,
        h2_co2_ratio=ratio,
        sweep_flow=sweep_flow,
        coolant_temp=coolant_temperature,
    )
