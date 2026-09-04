"""
Gas mixture physical, transport, and thermodynamic properties for E-Methanol reactor.
Species: CO2, H2, CO, CH3OH, H2O, N2
"""
import numpy as np
from typing import Dict, List, Tuple

# Species index mapping
SPECIES = ["CO2", "H2", "CO", "CH3OH", "H2O", "N2"]
SPECIES_IDX = {name: idx for idx, name in enumerate(SPECIES)}
MW = np.array([44.01, 2.016, 28.01, 32.04, 18.015, 28.013])  # g/mol -> [kg/kmol]

# Universal gas constant
R_GAS = 8.314462618  # J/(mol*K)

# Shomate / Polynomial parameters for Cp(T) in J/(mol*K)
# Cp(T) = A + B*(T/1000) + C*(T/1000)^2 + D*(T/1000)^3 + E/(T/1000)^2
# Valid for 300K - 1000K range (NIST WebBook / Perry's Chemical Engineers' Handbook)
CP_COEFFS = {
    # [A, B, C, D, E]
    "CO2": np.array([24.99735, 55.18696, -33.69137, 7.948387, -0.136638]),
    "H2": np.array([26.88865, 4.347029, -0.3267497, 0.03286182, 0.0875888]),
    "CO": np.array([25.56759, 6.096130, 4.054656, -2.671301, 0.131021]),
    "CH3OH": np.array([14.048, 183.15, -86.25, 14.83, 0.0]),
    "H2O": np.array([30.09200, 6.832514, 6.793435, -2.534480, 0.082139]),
    "N2": np.array([28.98641, 1.853978, -9.647459, 16.63537, 0.000117]),
}

# Reference standard enthalpies of formation at 298.15 K [J/mol]
# CO2: -393510, H2: 0, CO: -110530, CH3OH(g): -200670, H2O(g): -241820
HF_298 = {
    "CO2": -393510.0,
    "H2": 0.0,
    "CO": -110530.0,
    "CH3OH": -200670.0,
    "H2O": -241820.0,
    "N2": 0.0,
}


def get_pure_cp(species_name: str, T: float) -> float:
    """Calculates pure component ideal gas isobaric heat capacity Cp [J/(mol*K)]."""
    t = np.clip(T, 200.0, 1500.0) / 1000.0
    coeffs = CP_COEFFS[species_name]
    cp = coeffs[0] + coeffs[1]*t + coeffs[2]*(t**2) + coeffs[3]*(t**3) + coeffs[4]/(t**2 + 1e-6)
    return float(np.maximum(cp, 10.0))


def get_mixture_cp(mole_fractions: np.ndarray, T: float) -> float:
    """Calculates gas mixture molar heat capacity [J/(mol*K)]."""
    y = np.maximum(mole_fractions, 0.0)
    y_sum = np.sum(y)
    if y_sum > 0:
        y = y / y_sum
    else:
        y = np.array([0.2, 0.6, 0.0, 0.0, 0.0, 0.2])  # fallback

    cp_vals = np.array([get_pure_cp(sp, T) for sp in SPECIES[:len(mole_fractions)]])
    return float(np.sum(y * cp_vals))


def get_mixture_mw(mole_fractions: np.ndarray) -> float:
    """Calculates average mixture molecular weight [kg/kmol = g/mol]."""
    y = np.maximum(mole_fractions, 0.0)
    y_sum = np.sum(y)
    if y_sum > 0:
        y = y / y_sum
    mw_subset = MW[:len(mole_fractions)]
    return float(np.sum(y * mw_subset))


def get_gas_density(P_bar: float, T_K: float, mole_fractions: np.ndarray) -> float:
    """Calculates gas mixture density [kg/m^3] via Ideal Gas Law."""
    mw_kg_mol = get_mixture_mw(mole_fractions) * 1e-3  # kg/mol
    P_pa = P_bar * 1e5
    rho = (P_pa * mw_kg_mol) / (R_GAS * T_K)
    return float(np.maximum(rho, 1e-4))


def get_gas_viscosity(T_K: float) -> float:
    """
    Approximates gas mixture dynamic viscosity [Pa*s = kg/(m*s)] using Sutherland-type temperature dependence.
    Typical for syngas mixtures at 200-300 °C: ~2.0e-5 to 2.5e-5 Pa*s.
    """
    mu_ref = 2.0e-5  # Pa*s at 500 K
    T_ref = 500.0
    return float(mu_ref * ((T_K / T_ref) ** 0.7))
