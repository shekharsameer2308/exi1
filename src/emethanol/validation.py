"""
Conservation diagnostics and physical quality control validation for E-Methanol reactor.
"""
import numpy as np
from typing import Dict, Any, Tuple
from src.emethanol.thermodynamics import ELEMENT_MATRIX


def compute_elemental_balances(
    F_in: np.ndarray,
    F_out: np.ndarray,
    F_permeated: np.ndarray,
) -> Dict[str, float]:
    """
    Computes elemental conservation balance errors for Carbon, Hydrogen, and Oxygen.

    Parameters
    ----------
    F_in : np.ndarray
        Inlet species molar flow rates [mol/s] -> [CO2, H2, CO, MeOH, H2O]
    F_out : np.ndarray
        Outlet species molar flow rates [mol/s] -> [CO2, H2, CO, MeOH, H2O]
    F_permeated : np.ndarray
        Cumulative permeated molar flow rates across membrane [mol/s] -> [CO2, H2, CO, MeOH, H2O]

    Returns
    -------
    Dict[str, float]
        Relative conservation errors for C, H, O, and overall mass
    """
    # Matrix multiplication: moles of atoms = sum(F_i * element_count_i)
    # ELEMENT_MATRIX shape: (5, 3) -> [C, H, O]
    atoms_in = F_in[:5] @ ELEMENT_MATRIX
    atoms_out = (F_out[:5] + F_permeated[:5]) @ ELEMENT_MATRIX

    # Safe relative errors
    c_err = float(np.abs(atoms_in[0] - atoms_out[0]) / np.maximum(atoms_in[0], 1e-12))
    h_err = float(np.abs(atoms_in[1] - atoms_out[1]) / np.maximum(atoms_in[1], 1e-12))
    o_err = float(np.abs(atoms_in[2] - atoms_out[2]) / np.maximum(atoms_in[2], 1e-12))

    return {
        "carbon_balance_error": c_err,
        "hydrogen_balance_error": h_err,
        "oxygen_balance_error": o_err,
        "atoms_in_c": float(atoms_in[0]),
        "atoms_out_c": float(atoms_out[0]),
        "atoms_in_h": float(atoms_in[1]),
        "atoms_out_h": float(atoms_out[1]),
        "atoms_in_o": float(atoms_in[2]),
        "atoms_out_o": float(atoms_out[2]),
    }


def validate_simulation_physics(
    result_dict: Dict[str, Any],
    tolerance: float = 1e-3,
) -> Tuple[bool, str]:
    """
    Quality control filter to ensure physical plausibility of a simulation run.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, failure_reason)
    """
    if not result_dict.get("solver_success", False):
        return False, f"ODE Solver failed: {result_dict.get('solver_message', 'unknown')}"

    conv = result_dict.get("co2_conversion", -1.0)
    yield_meoh = result_dict.get("meoh_yield", -1.0)
    sel = result_dict.get("meoh_selectivity", -1.0)
    h2o_rem = result_dict.get("h2o_removal_fraction", 0.0)

    # Conversion / Yield bounds
    if not (-1e-5 <= conv <= 1.0 + 1e-5):
        return False, f"CO2 conversion out of bounds: {conv:.4f}"
    if not (-1e-5 <= yield_meoh <= 1.0 + 1e-5):
        return False, f"MeOH yield out of bounds: {yield_meoh:.4f}"
    if conv > 1e-4 and not (-1e-5 <= sel <= 1.0 + 1e-5):
        return False, f"MeOH selectivity out of bounds: {sel:.4f}"
    if not (-1e-5 <= h2o_rem <= 1.0 + 1e-5):
        return False, f"H2O removal fraction out of bounds: {h2o_rem:.4f}"

    # Elemental balances
    c_err = result_dict.get("carbon_balance_error", 1.0)
    h_err = result_dict.get("hydrogen_balance_error", 1.0)
    o_err = result_dict.get("oxygen_balance_error", 1.0)

    if c_err > tolerance:
        return False, f"Carbon balance error exceeded tolerance: {c_err:.2e} > {tolerance}"
    if h_err > tolerance:
        return False, f"Hydrogen balance error exceeded tolerance: {h_err:.2e} > {tolerance}"
    if o_err > tolerance:
        return False, f"Oxygen balance error exceeded tolerance: {o_err:.2e} > {tolerance}"

    return True, "PASSED"
