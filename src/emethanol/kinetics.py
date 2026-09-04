"""
Modular kinetic rate equations for CO2 hydrogenation to Methanol and Reverse Water-Gas Shift (RWGS).
Models supported:
1. "VBF": Vanden Bussche & Froment (1996) LHHW model.
2. "MIGNARD_PRITCHARD": Mignard & Pritchard (2008) modified LHHW model.
"""
import numpy as np
from typing import Tuple, Dict
from src.emethanol.properties import R_GAS
from src.emethanol.thermodynamics import get_equilibrium_constants


def calculate_rates(
    partial_pressures: np.ndarray,
    T_K: float,
    model: str = "VBF",
    catalyst_activity: float = 1.0,
) -> Tuple[float, float]:
    """
    Calculates intrinsic reaction rates [mol / (kg_cat * s)] for:
    r1: CO2 + 3H2 <=> CH3OH + H2O
    r2: CO2 + H2 <=> CO + H2O (RWGS)

    Parameters
    ----------
    partial_pressures : np.ndarray
        Array of partial pressures [bar] -> [p_CO2, p_H2, p_CO, p_CH3OH, p_H2O]
    T_K : float
        Absolute temperature in Kelvin [K]
    model : str
        Kinetic model formulation ("VBF" or "MIGNARD_PRITCHARD")
    catalyst_activity : float
        Deactivation / scaling factor (default 1.0)

    Returns
    -------
    Tuple[float, float]
        (r_meoh, r_rwgs) in [mol / (kg_cat * s)]
    """
    if T_K <= 0:
        raise ValueError("Absolute temperature must be strictly positive [K].")

    # Guard against negative or near-zero pressures to avoid numerical singularity
    p = np.maximum(partial_pressures[:5], 1e-12)
    p_CO2, p_H2, p_CO, p_MeOH, p_H2O = p[0], p[1], p[2], p[3], p[4]

    RT = R_GAS * T_K
    Keq1, Keq3 = get_equilibrium_constants(T_K, model=model)

    if model.upper() == "MIGNARD_PRITCHARD":
        # Mignard & Pritchard (2008) formulation (Chem. Eng. Res. Des. 86, 43-52)
        # Activation energy in kJ/mol converted to J/mol
        k5a = 1.07 * np.exp(36696.0 / RT)
        k1 = 1.22e6 * np.exp(-94765.0 / RT)
        
        K_H2O_KH2half = 6.62e-11 * np.exp(124119.0 / RT)
        K_H2half = 0.499 * np.exp(17197.0 / RT)
        K_H2O = 6.37e-9 * np.exp(113700.0 / RT)

        denom = (
            1.0
            + K_H2O_KH2half * (p_H2O / np.sqrt(p_H2))
            + K_H2half * np.sqrt(p_H2)
            + K_H2O * p_H2O
        )
        denom = np.maximum(denom, 1.0)

        df1 = 1.0 - (p_MeOH * p_H2O) / (Keq1 * p_CO2 * (p_H2 ** 3.0) + 1e-20)
        df2 = 1.0 - (p_CO * p_H2O) / (Keq3 * p_CO2 * p_H2 + 1e-20)

        r_meoh = catalyst_activity * (k5a * p_CO2 * np.sqrt(p_H2) * df1) / (denom ** 3.0)
        r_rwgs = catalyst_activity * (k1 * p_CO2 * df2) / denom

    else:
        # Standard Vanden Bussche & Froment (1996) formulation (J. Catalysis 161, 1-10)
        # k1 scaled to bar units: 1.22e10 * 1e-4 = 1.22e6
        k5a = 2.18e12 * np.exp(-87500.0 / RT)
        k1 = 1.22e6 * np.exp(-94765.0 / RT)
        
        K_H2O_KH2half = 6.62e-11 * np.exp(124119.0 / RT)
        K_H2half = 0.499 * np.exp(17197.0 / RT)
        K_H2O = 6.37e-9 * np.exp(113700.0 / RT)

        denom = (
            1.0
            + K_H2O_KH2half * (p_H2O / np.sqrt(p_H2))
            + K_H2half * np.sqrt(p_H2)
            + K_H2O * p_H2O
        )
        denom = np.maximum(denom, 1.0)

        df1 = 1.0 - (p_MeOH * p_H2O) / (Keq1 * p_CO2 * (p_H2 ** 3.0) + 1e-20)
        df2 = 1.0 - (p_CO * p_H2O) / (Keq3 * p_CO2 * p_H2 + 1e-20)

        r_meoh = catalyst_activity * (k5a * p_CO2 * p_H2 * df1) / (denom ** 3.0)
        r_rwgs = catalyst_activity * (k1 * p_CO2 * p_H2 * df2) / denom

    r_meoh = float(np.clip(r_meoh, -100.0, 100.0))
    r_rwgs = float(np.clip(r_rwgs, -100.0, 100.0))

    return r_meoh, r_rwgs
