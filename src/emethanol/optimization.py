"""
Reactor optimization engine with surrogate screening and mandatory physics engine verification.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, Callable
from scipy.optimize import minimize

from src.emethanol.reactor import simulate_reactor, ReactorSimulationResult, ModelConfig


# Default operational bounds
OPTIMIZATION_BOUNDS = {
    "T_in_K": (463.15, 533.15),       # 190 °C - 260 °C
    "P_in_bar": (30.0, 80.0),          # 30 - 80 bar
    "flow_mol_s": (0.008, 0.030),      # 0.008 - 0.030 mol/s
    "h2_co2_ratio": (2.5, 4.5),        # 2.5 - 4.5
    "water_permeance": (0.5e-7, 3.0e-7)# 0.5e-7 - 3.0e-7 mol/(m^2*s*Pa)
}


def is_in_training_domain(
    inputs: Dict[str, float],
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Tuple[bool, str]:
    """
    Evaluates whether input parameters lie strictly within the surrogate training domain (interpolation)
    or fall outside (extrapolation hazard).
    """
    b = bounds or OPTIMIZATION_BOUNDS
    for key, (low, high) in b.items():
        val = inputs.get(key, None)
        if val is None:
            continue
        if val < low - 1e-4 or val > high + 1e-4:
            return False, f"Extrapolation Warning: {key}={val:.3f} is outside training domain [{low:.2f}, {high:.2f}]"
    return True, "Interpolation: Within safe training domain"


def optimize_reactor_physics(
    objective: str = "max_yield",
    min_selectivity: float = 0.80,
    max_temperature_K: float = 550.0,
    fixed_conditions: Optional[Dict[str, Any]] = None,
    surrogate_model: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Performs constrained numerical optimization to maximize methanol yield,
    verified directly against the 1D non-isothermal physics engine.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing optimal conditions, verified physics metrics, surrogate metrics, and residuals.
    """
    cond = {
        "reactor_length": 1.0,
        "reactor_diameter": 0.02,
        "kinetic_model": "VBF",
        "membrane_model": "LDF",
        "membrane_enabled": True,
        "non_isothermal": True,
        "pressure_drop": False,
    }
    if fixed_conditions:
        cond.update(fixed_conditions)

    # Initial guess [T_in, P_in, flow, ratio, permeance]
    x0 = np.array([493.15, 60.0, 0.015, 3.0, 1.5e-7])
    bounds = [
        OPTIMIZATION_BOUNDS["T_in_K"],
        OPTIMIZATION_BOUNDS["P_in_bar"],
        OPTIMIZATION_BOUNDS["flow_mol_s"],
        OPTIMIZATION_BOUNDS["h2_co2_ratio"],
        OPTIMIZATION_BOUNDS["water_permeance"],
    ]

    def cost_func(x: np.ndarray) -> float:
        T_in, P_in, flow, ratio, perm = x
        res = simulate_reactor(
            temperature=float(T_in),
            pressure=float(P_in),
            total_flow=float(flow),
            h2_co2_ratio=float(ratio),
            water_permeance=float(perm),
            **cond
        )
        if not res.solver_success:
            return 100.0  # Heavy penalty

        # Objective: Maximize MeOH Yield -> minimize -meoh_yield
        penalty = 0.0
        if res.meoh_selectivity < min_selectivity:
            penalty += 10.0 * (min_selectivity - res.meoh_selectivity)
        if res.max_temperature > max_temperature_K:
            penalty += 1.0 * (res.max_temperature - max_temperature_K)

        return float(-res.meoh_yield + penalty)

    # Run Powell / Nelder-Mead / L-BFGS-B optimization
    opt_res = minimize(cost_func, x0, bounds=bounds, method="L-BFGS-B", options={"maxiter": 30, "ftol": 1e-4})

    opt_x = opt_res.x
    optimal_conditions = {
        "T_in_K": float(opt_x[0]),
        "P_in_bar": float(opt_x[1]),
        "flow_mol_s": float(opt_x[2]),
        "h2_co2_ratio": float(opt_x[3]),
        "water_permeance": float(opt_x[4]),
    }

    # MANDATORY VERIFICATION: Re-simulate the candidate optimal point through physics engine
    verified_physics = simulate_reactor(
        temperature=optimal_conditions["T_in_K"],
        pressure=optimal_conditions["P_in_bar"],
        total_flow=optimal_conditions["flow_mol_s"],
        h2_co2_ratio=optimal_conditions["h2_co2_ratio"],
        water_permeance=optimal_conditions["water_permeance"],
        **cond
    )

    # If surrogate model supplied, compare prediction vs physics
    surrogate_pred = {}
    prediction_errors = {}
    if surrogate_model is not None:
        try:
            X_df = pd.DataFrame([{
                "T_in_K": optimal_conditions["T_in_K"],
                "P_in_bar": optimal_conditions["P_in_bar"],
                "h2_co2_ratio": optimal_conditions["h2_co2_ratio"],
                "flow_mol_s": optimal_conditions["flow_mol_s"],
            }])
            preds = surrogate_model.predict(X_df)[0]
            surrogate_pred = {
                "co2_conversion": float(preds[0]),
                "meoh_yield": float(preds[1]),
            }
            prediction_errors = {
                "co2_conversion_error": float(abs(surrogate_pred["co2_conversion"] - verified_physics.co2_conversion)),
                "meoh_yield_error": float(abs(surrogate_pred["meoh_yield"] - verified_physics.meoh_yield)),
            }
        except Exception as e:
            surrogate_pred = {"error": str(e)}

    return {
        "optimal_conditions": optimal_conditions,
        "physics_result": verified_physics.to_dict(),
        "surrogate_result": surrogate_pred,
        "prediction_error": prediction_errors,
        "optimization_success": opt_res.success,
        "optimization_message": opt_res.message,
    }
