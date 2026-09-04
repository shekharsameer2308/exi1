"""
Thermodynamic equilibrium constants, reaction enthalpies, and stoichiometric matrices for E-Methanol reactor.
"""
import numpy as np
from typing import Tuple, Dict
from src.emethanol.properties import R_GAS, HF_298, get_pure_cp

# Stoichiometric Matrix S for primary 5 species: [CO2, H2, CO, CH3OH, H2O]
# Row 0: Reaction 1 (CO2 + 3H2 <=> CH3OH + H2O)
# Row 1: Reaction 2 (CO2 + H2 <=> CO + H2O)
STOICHIOMETRIC_MATRIX = np.array([
    [-1.0, -3.0,  0.0,  1.0,  1.0],  # Rxn 1: MeOH synthesis
    [-1.0, -1.0,  1.0,  0.0,  1.0],  # Rxn 2: RWGS
])

# Elemental Composition Matrix (Carbon, Hydrogen, Oxygen atoms per molecule)
# Columns: [CO2, H2, CO, CH3OH, H2O]
ELEMENT_MATRIX = np.array([
    # C,  H,  O
    [1.0, 0.0, 2.0],  # CO2
    [0.0, 2.0, 0.0],  # H2
    [1.0, 0.0, 1.0],  # CO
    [1.0, 4.0, 1.0],  # CH3OH
    [0.0, 2.0, 1.0],  # H2O
])


def get_equilibrium_constants(T_K: float, model: str = "VBF") -> Tuple[float, float]:
    """
    Calculates thermodynamic equilibrium constants for MeOH synthesis and RWGS.
    
    Keq1: CO2 + 3H2 <=> CH3OH + H2O  [bar^-2]
    Keq3: CO2 + H2 <=> CO + H2O       [dimensionless]
    
    References:
    - Vanden Bussche & Froment (1996) J. Catalysis 161, 1-10
    - Graaf et al. (1986) Chem. Eng. Sci. 41(11), 2883-2890
    - Mignard & Pritchard (2008) Chem. Eng. Res. Des. 86, 43-52
    """
    T = np.clip(T_K, 200.0, 1500.0)
    
    if model.upper() in ["VBF", "MIGNARD_PRITCHARD"]:
        log10_Keq1 = 3066.0 / T - 10.592
        log10_Keq3 = -2073.0 / T + 2.029
        Keq1 = float(10.0 ** log10_Keq1)
        Keq3 = float(10.0 ** log10_Keq3)
    else:
        # Fallback to standard VBF
        log10_Keq1 = 3066.0 / T - 10.592
        log10_Keq3 = -2073.0 / T + 2.029
        Keq1 = float(10.0 ** log10_Keq1)
        Keq3 = float(10.0 ** log10_Keq3)
        
    return float(np.maximum(Keq1, 1e-15)), float(np.maximum(Keq3, 1e-15))


def get_reaction_enthalpies(T_K: float) -> Tuple[float, float]:
    """
    Calculates temperature-dependent standard enthalpies of reaction ΔH_rxn [J/mol].
    Rxn 1: CO2 + 3H2 -> CH3OH + H2O  (Exothermic, ΔH_298 ~ -49.5 kJ/mol)
    Rxn 2: CO2 + H2 -> CO + H2O      (Endothermic, ΔH_298 ~ +41.2 kJ/mol)
    """
    # Base enthalpies at 298.15 K
    dH1_298 = HF_298["CH3OH"] + HF_298["H2O"] - HF_298["CO2"] - 3.0 * HF_298["H2"]  # ~ -48980 J/mol
    dH2_298 = HF_298["CO"] + HF_298["H2O"] - HF_298["CO2"] - HF_298["H2"]           # ~ +41160 J/mol
    
    # Kirchhoff integration approximation at mean temperature: ΔCp * (T - 298.15)
    T_mid = 0.5 * (298.15 + np.clip(T_K, 298.15, 1000.0))
    
    cp_co2 = get_pure_cp("CO2", T_mid)
    cp_h2 = get_pure_cp("H2", T_mid)
    cp_co = get_pure_cp("CO", T_mid)
    cp_meoh = get_pure_cp("CH3OH", T_mid)
    cp_h2o = get_pure_cp("H2O", T_mid)
    
    dCp_1 = cp_meoh + cp_h2o - cp_co2 - 3.0 * cp_h2
    dCp_2 = cp_co + cp_h2o - cp_co2 - cp_h2
    
    dT = T_K - 298.15
    dH1 = dH1_298 + dCp_1 * dT
    dH2 = dH2_298 + dCp_2 * dT
    
    return float(dH1), float(dH2)
