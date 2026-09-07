"""
Reaction Kinetics Module for CO2 Hydrogenation to Methanol.
Implements Vanden Bussche & Froment (1996) LHHW kinetics with catalyst
preservation envelope constraints.
"""
from typing import Tuple, Dict
import numpy as np
from core.thermodynamics import get_equilibrium_constants, R_GAS


def calculate_reaction_rates(
    p_partial_bar: np.ndarray,
    T_K: float,
    catalyst_activity: float = 1.0,
    eta_meoh: float = 0.85,
    eta_rwgs: float = 0.90,
) -> Tuple[float, float, Dict[str, float]]:
    """
    Computes reaction rates r_MeOH and r_RWGS in mol / (kg_cat * s).
    
    Parameters
    ----------
    p_partial_bar : np.ndarray
        Partial pressures of [CO2, H2, CO, CH3OH, H2O, N2] in bar.
    T_K : float
        Local bed temperature in Kelvin.
    catalyst_activity : float
        Learned or scaled catalyst deactivation factor a(t) in [0, 1].
    eta_meoh : float
        Internal pellet effectiveness factor for methanol reaction.
    eta_rwgs : float
        Internal pellet effectiveness factor for RWGS reaction.
        
    Returns
    -------
    r_meoh : float
        Rate of methanol formation [mol / (kg_cat * s)].
    r_rwgs : float
        Rate of RWGS reaction [mol / (kg_cat * s)].
    info : dict
        Driving forces and preservation metrics.
    """
    # Guard against negative or infinitesimal pressures to avoid numerical singularity
    p = np.maximum(p_partial_bar[:5], 1e-12)
    p_co2, p_h2, p_co, p_meoh, p_h2o = p[0], p[1], p[2], p[3], p[4]
    
    RT = R_GAS * T_K
    Keq1, Keq2 = get_equilibrium_constants(T_K)
    
    # Rate constants (Vanden Bussche & Froment 1996)
    k5a = 2.18e12 * np.exp(-87500.0 / RT)
    k1 = 1.22e6 * np.exp(-94765.0 / RT)
    
    # Adsorption parameters
    K_H2O_KH2half = 6.62e-11 * np.exp(124119.0 / RT)
    K_H2half = 0.499 * np.exp(17197.0 / RT)
    K_H2O = 6.37e-9 * np.exp(113700.0 / RT)
    
    # Denominator for competitive site adsorption
    denom = (
        1.0
        + K_H2O_KH2half * (p_h2o / np.sqrt(p_h2))
        + K_H2half * np.sqrt(p_h2)
        + K_H2O * p_h2o
    )
    denom = np.maximum(denom, 1.0)
    
    # Driving forces
    df1 = 1.0 - (p_meoh * p_h2o) / (Keq1 * p_co2 * (p_h2**3.0) + 1e-20)
    df2 = 1.0 - (p_co * p_h2o) / (Keq2 * p_co2 * p_h2 + 1e-20)
    
    # Rates [mol / (kg_cat * s)]
    r_meoh_intrinsic = (k5a * p_co2 * p_h2 * df1) / (denom**3.0)
    r_rwgs_intrinsic = (k1 * p_co2 * p_h2 * df2) / denom
    
    r_meoh = catalyst_activity * eta_meoh * r_meoh_intrinsic
    r_rwgs = catalyst_activity * eta_rwgs * r_rwgs_intrinsic
    
    r_meoh = float(np.clip(r_meoh, -50.0, 50.0))
    r_rwgs = float(np.clip(r_rwgs, -50.0, 50.0))
    
    info = {
        "k5a": k5a,
        "k1": k1,
        "Keq1": Keq1,
        "Keq2": Keq2,
        "driving_force_meoh": df1,
        "driving_force_rwgs": df2,
        "p_h2o_bar": p_h2o,
    }
    return r_meoh, r_rwgs, info


def check_catalyst_preservation(
    p_h2o_bar: float,
    P_total_bar: float,
    min_water_fraction: float = 0.015,
) -> Tuple[bool, float, str]:
    """
    Evaluates whether the catalyst operating state satisfies the active Cu+
    preservation boundary to prevent brass formation and zinc migration.
    """
    min_p_h2o = min_water_fraction * P_total_bar
    is_safe = p_h2o_bar >= min_p_h2o
    margin = p_h2o_bar - min_p_h2o
    status = "PRESERVED" if is_safe else "WARNING_DEACTIVATION_RISK"
    return is_safe, margin, status
