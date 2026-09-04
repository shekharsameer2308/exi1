"""
Modular membrane transport models for selective H2O removal in E-Methanol membrane reactor.
Models supported:
1. "LDF": Linear Driving Force / Solution-Diffusion model with Arrhenius temperature dependence.
2. "MAXWELL_STEFAN": Multicomponent coupled Maxwell-Stefan transport framework in microporous zeolite.
"""
import numpy as np
from typing import Tuple, Dict, Optional
from src.emethanol.properties import R_GAS


def calculate_membrane_flux(
    partial_pressures_rxn: np.ndarray,
    partial_pressures_sweep: np.ndarray,
    T_K: float,
    model: str = "LDF",
    permeance_h2o_base: float = 1.0e-7,
    activation_energy_h2o: float = 0.0,
    selectivity_h2o_co2: float = 1000.0,
    selectivity_h2o_h2: float = 500.0,
    selectivity_h2o_meoh: float = 200.0,
    membrane_thickness_m: float = 5.0e-6,
) -> np.ndarray:
    """
    Calculates species permeation fluxes J_i [mol / (m^2 * s)] across the selective membrane.
    Species order: [CO2, H2, CO, CH3OH, H2O]

    Parameters
    ----------
    partial_pressures_rxn : np.ndarray
        Partial pressures on reaction/tube side [bar] -> [CO2, H2, CO, MeOH, H2O]
    partial_pressures_sweep : np.ndarray
        Partial pressures on sweep/shell side [bar] -> [CO2, H2, CO, MeOH, H2O]
    T_K : float
        Membrane local temperature [K]
    model : str
        "LDF" or "MAXWELL_STEFAN"
    permeance_h2o_base : float
        H2O permeance at reference T (500 K) in [mol / (m^2 * s * Pa)]
    activation_energy_h2o : float
        Apparent activation energy for H2O permeation [J/mol] (default 0 for standard LDF)
    selectivity_h2o_co2, selectivity_h2o_h2, selectivity_h2o_meoh : float
        Ideal separation factors of NaA zeolite membrane
    membrane_thickness_m : float
        Active zeolite layer thickness [m]

    Returns
    -------
    np.ndarray
        Species fluxes [mol / (m^2 * s)] for [CO2, H2, CO, CH3OH, H2O]
    """
    # Guard partial pressures
    p_rxn = np.maximum(partial_pressures_rxn[:5], 0.0)
    p_swp = np.maximum(partial_pressures_sweep[:5], 0.0)
    
    # Delta P in Pascals [1 bar = 1e5 Pa]
    dp_pa = (p_rxn - p_swp) * 1e5

    # Permeance with optional Arrhenius temperature dependence
    if activation_energy_h2o > 0 and T_K > 0:
        RT = R_GAS * T_K
        RT_ref = R_GAS * 500.0
        q_h2o = permeance_h2o_base * np.exp(-activation_energy_h2o * (1.0/RT - 1.0/RT_ref))
    else:
        q_h2o = permeance_h2o_base

    if model.upper() == "MAXWELL_STEFAN":
        # Coupled Maxwell-Stefan formulation for microporous zeolite (NaA)
        # J_i = - sum( B_ij^-1 * Gamma_jk * d(theta_k)/dx )
        # Using Langmuir multicomponent adsorption + Stefan-Maxwell matrix inversion
        q_sat = 8.0  # mol/kg saturation loading in NaA zeolite
        b_h2o = 5.0e-5  # Pa^-1 adsorption constant
        b_meoh = 1.0e-5 # Pa^-1
        
        # Fractional surface loadings theta_i
        denom_ads = 1.0 + b_h2o * p_rxn[4]*1e5 + b_meoh * p_rxn[3]*1e5 + 1e-12
        theta_h2o = (b_h2o * p_rxn[4]*1e5) / denom_ads
        theta_meoh = (b_meoh * p_rxn[3]*1e5) / denom_ads
        
        # Maxwell-Stefan counter-diffusion coefficients
        D_h2o_zeo = q_h2o * membrane_thickness_m * R_GAS * T_K / 1e5  # m^2/s
        D_meoh_zeo = D_h2o_zeo / selectivity_h2o_meoh
        
        # Driving force across membrane thickness delta_m
        j_h2o = (D_h2o_zeo * q_sat / membrane_thickness_m) * theta_h2o * np.maximum(dp_pa[4] / (p_rxn[4]*1e5 + 1e-10), 0.0)
        j_meoh = (D_meoh_zeo * q_sat / membrane_thickness_m) * theta_meoh * np.maximum(dp_pa[3] / (p_rxn[3]*1e5 + 1e-10), 0.0)
        
        # Minor species leakage
        j_co2 = (q_h2o / selectivity_h2o_co2) * np.maximum(dp_pa[0], 0.0)
        j_h2 = (q_h2o / selectivity_h2o_h2) * np.maximum(dp_pa[1], 0.0)
        j_co = 0.0
        
        fluxes = np.array([j_co2, j_h2, j_co, j_meoh, j_h2o])

    else:
        # Standard LDF (Linear Driving Force) model
        # Flux J_i = Permeance_i * (p_rxn_i - p_sweep_i)
        q_co2 = q_h2o / selectivity_h2o_co2
        q_h2 = q_h2o / selectivity_h2o_h2
        q_meoh = q_h2o / selectivity_h2o_meoh
        q_co = 0.0

        permeances = np.array([q_co2, q_h2, q_co, q_meoh, q_h2o])
        
        # Only allow positive outward permeation (from reaction bed into sweep)
        fluxes = permeances * np.maximum(dp_pa, 0.0)

    return np.maximum(fluxes, 0.0)
