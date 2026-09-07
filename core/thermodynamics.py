"""
Thermodynamic Package for CO2 Hydrogenation to E-Methanol.
Includes Peng-Robinson Equation of State, NASA polynomial heat capacities,
and chemical equilibrium constants.
"""
from typing import Dict, Tuple, List
import numpy as np

# Gas Constant
R_GAS = 8.314462618  # J / (mol * K)

# Species index mapping
SPECIES = ["CO2", "H2", "CO", "CH3OH", "H2O", "N2"]
SPECIES_IDX = {name: i for i, name in enumerate(SPECIES)}
N_SPECIES = len(SPECIES)

# Molecular weights [kg / mol]
MOLAR_MASSES = np.array([
    0.04401,   # CO2
    0.002016,  # H2
    0.02801,   # CO
    0.03204,   # CH3OH
    0.018015,  # H2O
    0.028013,  # N2
])

# Critical parameters: [Tc (K), Pc (Pa), omega (acentric factor)]
CRITICAL_PROPS = {
    "CO2": (304.13, 7.375e6, 0.224),
    "H2": (33.145, 1.296e6, -0.216),
    "CO": (132.86, 3.494e6, 0.048),
    "CH3OH": (512.6, 8.09e6, 0.565),
    "H2O": (647.14, 22.064e6, 0.344),
    "N2": (126.19, 3.396e6, 0.037),
}

# NASA 7-coefficient polynomials for Cp / R = a0 + a1*T + a2*T^2 + a3*T^3 + a4*T^4
# Valid for T in [300 K, 1000 K]
NASA_CP_COEFFS = {
    "CO2": np.array([2.35677352e0, 8.98459677e-3, -7.12356269e-6, 2.45919022e-9, -1.43699548e-13]),
    "H2": np.array([3.2981240e0, 8.2494417e-4, -8.1430155e-7, -9.4754343e-11, 4.1348722e-13]),
    "CO": np.array([3.2624516e0, 1.5119409e-3, -3.8817556e-6, 5.5819442e-9, -2.4749514e-12]),
    "CH3OH": np.array([2.660104e0, 1.638841e-2, -6.643764e-6, -1.189512e-9, 1.344795e-12]),
    "H2O": np.array([4.19864056e0, -2.03663310e-3, 6.52040211e-6, -5.48797062e-9, 1.77197812e-12]),
    "N2": np.array([3.53100528e0, -1.23660988e-4, -5.02999433e-7, 2.43530612e-9, -1.40881235e-12]),
}

# Standard enthalpies of formation at 298.15 K [J / mol]
HF_298 = np.array([
    -393.51e3,  # CO2
    0.0,        # H2
    -110.53e3,  # CO
    -200.66e3,  # CH3OH (gas)
    -241.82e3,  # H2O (gas)
    0.0,        # N2
])


def get_pure_heat_capacity(species: str, T_K: float) -> float:
    """Returns pure component gas Cp in J / (mol * K)."""
    coeffs = NASA_CP_COEFFS[species]
    T_vec = np.array([1.0, T_K, T_K**2, T_K**3, T_K**4])
    return float(R_GAS * np.dot(coeffs, T_vec))


def get_mixture_heat_capacity(y: np.ndarray, T_K: float) -> float:
    """Calculates molar heat capacity of gas mixture in J / (mol * K)."""
    cps = np.array([get_pure_heat_capacity(sp, T_K) for sp in SPECIES])
    return float(np.sum(y * cps))


def get_reaction_enthalpies(T_K: float) -> Tuple[float, float]:
    """
    Returns standard reaction enthalpies at temperature T_K in J / mol.
    dH_rxn1: CO2 + 3 H2 <=> CH3OH + H2O
    dH_rxn2: CO2 + H2 <=> CO + H2O
    """
    # Baseline at 298.15 K
    dH1_298 = -49.50e3  # J / mol
    dH2_298 = 41.20e3   # J / mol
    
    # Integrate delta Cp from 298.15 to T_K
    T_mid = 0.5 * (298.15 + T_K)
    cp_co2 = get_pure_heat_capacity("CO2", T_mid)
    cp_h2 = get_pure_heat_capacity("H2", T_mid)
    cp_co = get_pure_heat_capacity("CO", T_mid)
    cp_meoh = get_pure_heat_capacity("CH3OH", T_mid)
    cp_h2o = get_pure_heat_capacity("H2O", T_mid)
    
    dCp1 = (cp_meoh + cp_h2o) - (cp_co2 + 3.0 * cp_h2)
    dCp2 = (cp_co + cp_h2o) - (cp_co2 + cp_h2)
    
    dT = T_K - 298.15
    dH1 = dH1_298 + dCp1 * dT
    dH2 = dH2_298 + dCp2 * dT
    return dH1, dH2


def get_equilibrium_constants(T_K: float) -> Tuple[float, float]:
    """
    Calculates equilibrium constants for Methanol synthesis and RWGS.
    Keq1 in bar^-2, Keq2 dimensionless.
    Reference: Graaf et al. / Vanden Bussche & Froment
    """
    log10_Keq1 = 3066.0 / T_K - 10.592
    Keq1 = 10.0 ** log10_Keq1  # bar^-2
    
    log10_Keq2 = -2073.0 / T_K + 2.029
    Keq2 = 10.0 ** log10_Keq2  # dimensionless
    
    return Keq1, Keq2


def peng_robinson_compressibility(y: np.ndarray, T_K: float, P_Pa: float) -> Tuple[float, float]:
    """
    Computes Peng-Robinson Z-factor and mixture density [kg / m^3].
    """
    P_bar = P_Pa / 1e5
    N = len(SPECIES)
    a_pure = np.zeros(N)
    b_pure = np.zeros(N)
    
    for i, sp in enumerate(SPECIES):
        Tc, Pc, omega = CRITICAL_PROPS[sp]
        Tr = T_K / Tc
        m_i = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
        alpha_i = (1.0 + m_i * (1.0 - np.sqrt(Tr)))**2
        a_pure[i] = 0.45724 * (R_GAS * Tc)**2 / Pc * alpha_i
        b_pure[i] = 0.07780 * (R_GAS * Tc) / Pc
        
    # Van der Waals mixing rules (kij assumed 0 for baseline fast solve)
    a_mix = np.sum(np.outer(y, y) * np.sqrt(np.outer(a_pure, a_pure)))
    b_mix = np.sum(y * b_pure)
    
    A = a_mix * P_Pa / (R_GAS * T_K)**2
    B = b_mix * P_Pa / (R_GAS * T_K)
    
    # Cubic equation: Z^3 - (1-B)*Z^2 + (A - 3B^2 - 2B)*Z - (AB - B^2 - B^3) = 0
    c3 = 1.0
    c2 = -(1.0 - B)
    c1 = A - 3.0 * B**2 - 2.0 * B
    c0 = -(A * B - B**2 - B**3)
    
    roots = np.roots([c3, c2, c1, c0])
    real_roots = roots[np.isreal(roots)].real
    valid_roots = real_roots[real_roots > B]
    
    Z = float(np.max(valid_roots)) if len(valid_roots) > 0 else 1.0
    
    # Mixture molecular weight
    MW_mix = np.sum(y * MOLAR_MASSES)
    rho_kg_m3 = (P_Pa * MW_mix) / (Z * R_GAS * T_K)
    
    return Z, rho_kg_m3
