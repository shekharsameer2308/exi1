"""
Differential mass, energy, momentum, and multicomponent permeation balances for 1D packed-bed membrane reactor.
"""
import numpy as np
from typing import Tuple, Dict, Optional
from src.emethanol.properties import R_GAS, get_mixture_cp, get_gas_density, get_gas_viscosity
from src.emethanol.thermodynamics import STOICHIOMETRIC_MATRIX, get_reaction_enthalpies
from src.emethanol.kinetics import calculate_rates
from src.emethanol.membrane import calculate_membrane_flux


def evaluate_derivatives(
    z: float,
    state: np.ndarray,
    reactor_diameter: float,
    catalyst_density: float,
    void_fraction: float,
    particle_diameter: float,
    overall_heat_transfer_coeff: float,
    coolant_temperature: float,
    sweep_partial_pressures: np.ndarray,
    kinetic_model: str = "VBF",
    membrane_model: str = "LDF",
    membrane_enabled: bool = True,
    water_permeance: float = 1e-7,
    membrane_activation_energy: float = 0.0,
    non_isothermal: bool = True,
    pressure_drop: bool = False,
) -> np.ndarray:
    """
    Evaluates ODE derivative vector d(state)/dz along the reactor axis.
    
    State Vector (length 12):
    state[0..4]: F_CO2, F_H2, F_CO, F_CH3OH, F_H2O in reactor tube [mol/s]
    state[5]: T [K]
    state[6]: P [bar]
    state[7..11]: Cumulative permeated molar flow F_perm for [CO2, H2, CO, CH3OH, H2O] [mol/s]

    Returns
    -------
    np.ndarray
        Array of 12 state derivatives.
    """
    F = np.maximum(state[:5], 1e-15)
    T = float(np.clip(state[5], 250.0, 1000.0))
    P = float(np.clip(state[6], 1.0, 200.0))

    F_tot = float(np.sum(F))
    y = F / F_tot
    p_partial = y * P  # [bar]

    # Reactor geometry
    A_cs = np.pi * (reactor_diameter ** 2) / 4.0
    perimeter = np.pi * reactor_diameter

    # 1. Reaction Kinetics
    r_meoh, r_rwgs = calculate_rates(p_partial, T, model=kinetic_model)
    rates = np.array([r_meoh, r_rwgs])
    
    # Generation rate per unit length: rho_cat * A_cs * (S.T @ rates) [mol/(m*s)]
    r_gen = catalyst_density * A_cs * (STOICHIOMETRIC_MATRIX.T @ rates)

    # 2. Membrane Permeation
    if membrane_enabled:
        fluxes = calculate_membrane_flux(
            partial_pressures_rxn=p_partial,
            partial_pressures_sweep=sweep_partial_pressures,
            T_K=T,
            model=membrane_model,
            permeance_h2o_base=water_permeance,
            activation_energy_h2o=membrane_activation_energy,
        )
        r_loss = perimeter * fluxes
    else:
        fluxes = np.zeros(5)
        r_loss = np.zeros(5)

    # Species mass balance: dF/dz = r_gen - r_loss
    dF_dz = r_gen - r_loss
    dF_perm_dz = r_loss  # Permeated species flow rate derivatives [mol/(m*s)]

    # 3. Energy Balance: dT/dz
    if non_isothermal:
        dH1, dH2 = get_reaction_enthalpies(T)
        q_gen = catalyst_density * A_cs * ((-dH1) * r_meoh + (-dH2) * r_rwgs)
        q_cool = overall_heat_transfer_coeff * perimeter * (T - coolant_temperature)
        
        Cp_mix = get_mixture_cp(y, T)
        thermal_capacity = np.maximum(F_tot * Cp_mix, 1e-3)
        
        dT_dz = (q_gen - q_cool) / thermal_capacity
    else:
        dT_dz = 0.0

    # 4. Momentum Balance (Ergun Equation): dP/dz
    if pressure_drop:
        rho_gas = get_gas_density(P, T, y)
        mu_gas = get_gas_viscosity(T)
        
        Q_vol = (F_tot * R_GAS * T) / (P * 1e5)  # m^3/s
        u_s = Q_vol / A_cs  # m/s
        
        eps = void_fraction
        dp = particle_diameter
        
        term_visc = 150.0 * (((1.0 - eps) ** 2) / (eps ** 3)) * (mu_gas * u_s / (dp ** 2))
        term_inert = 1.75 * ((1.0 - eps) / (eps ** 3)) * (rho_gas * (u_s ** 2) / dp)
        
        dP_dz_pa_m = -(term_visc + term_inert)
        dP_dz = dP_dz_pa_m * 1e-5  # bar/m
    else:
        dP_dz = 0.0

    return np.concatenate([dF_dz, [dT_dz, dP_dz], dF_perm_dz])
