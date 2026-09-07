"""
2D Transport Phenomena Module.
Computes radial dispersion, effective radial thermal conductivity,
wall heat transfer coefficients, and dynamic Ergun velocity updates.
"""
from typing import Tuple
import numpy as np
from core.thermodynamics import R_GAS, SPECIES, MOLAR_MASSES, get_mixture_heat_capacity, peng_robinson_compressibility


def compute_radial_dispersion(
    u_s: float,
    d_p: float,
    D_m: float = 2.0e-5,
    eps: float = 0.40,
) -> float:
    """
    Computes effective radial dispersion coefficient D_er [m^2 / s].
    Using standard packed bed correlation: 1/P_er = 1/P_er,inf + 1/(alpha * Sc * Re)
    Typically: D_er ~ (u_s * d_p) / 10 + eps * D_m
    """
    Pe_r = 10.0  # Radial Peclet number in turbulent/transitional packed beds
    D_er = (u_s * d_p) / Pe_r + eps * D_m
    return float(D_er)


def compute_effective_radial_conductivity(
    u_s: float,
    rho_g: float,
    Cp_g: float,
    d_p: float,
    k_g: float = 0.05,
    k_s: float = 0.30,
    eps: float = 0.40,
) -> float:
    """
    Computes effective radial thermal conductivity k_er [W / (m * K)].
    k_er = k_bed_static + (rho_g * Cp_g * u_s * d_p) / Pe_hr
    """
    k_bed_static = eps * k_g + (1.0 - eps) * k_s
    Pe_hr = 8.0  # Radial thermal Peclet number
    k_er = k_bed_static + (rho_g * Cp_g * u_s * d_p) / Pe_hr
    return float(k_er)


def compute_wall_heat_transfer_coefficient(
    u_s: float,
    rho_g: float,
    mu_g: float,
    Cp_g: float,
    k_g: float,
    d_p: float,
    d_t: float,
) -> float:
    """
    Computes overall wall heat transfer coefficient U_wall [W / (m^2 * K)]
    combining bed wall resistance and coolant jacket convection.
    """
    Re_p = (rho_g * u_s * d_p) / max(mu_g, 1e-6)
    Pr = (mu_g * Cp_g) / max(k_g, 1e-4)
    
    # Leva / Dixon-Cresswell correlation for packed tube wall heat transfer
    Nu_w = 0.20 * (Re_p ** 0.8) * (Pr ** 0.33) * (d_p / d_t) ** 0.2
    h_w = Nu_w * k_g / d_p
    
    # Jacket external boiling water coolant side
    h_coolant = 2500.0  # W / (m^2 * K)
    
    # Combined overall U
    U_wall = 1.0 / (1.0 / max(h_w, 50.0) + 1.0 / h_coolant)
    return float(min(U_wall, 450.0))


def compute_mixture_viscosity(y: np.ndarray, T_K: float) -> float:
    """
    Computes gas dynamic viscosity [Pa * s] via Wilke's semi-empirical mixing rule.
    """
    # Pure component viscosity correlations (Sutherland-like / power law)
    # in 1e-6 Pa*s at T_K
    mu_pure = np.array([
        1.48e-5 * (T_K / 293.15)**0.75,  # CO2
        8.80e-6 * (T_K / 293.15)**0.68,  # H2
        1.75e-5 * (T_K / 293.15)**0.72,  # CO
        1.20e-5 * (T_K / 293.15)**0.78,  # CH3OH
        1.25e-5 * (T_K / 293.15)**0.80,  # H2O
        1.78e-5 * (T_K / 293.15)**0.70,  # N2
    ])
    
    N = len(SPECIES)
    phi = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            num = (1.0 + np.sqrt(mu_pure[i] / mu_pure[j]) * (MOLAR_MASSES[j] / MOLAR_MASSES[i])**0.25)**2
            denom = np.sqrt(8.0 * (1.0 + MOLAR_MASSES[i] / MOLAR_MASSES[j]))
            phi[i, j] = num / denom
            
    mu_mix = 0.0
    for i in range(N):
        denom_sum = np.sum(y * phi[i, :])
        mu_mix += (y[i] * mu_pure[i]) / max(denom_sum, 1e-8)
        
    return float(mu_mix)


def update_dynamic_ergun(
    F_ret_total: float,
    y_ret: np.ndarray,
    T_K: float,
    P_Pa: float,
    A_c: float,
    d_p: float = 0.003,
    eps: float = 0.40,
) -> Tuple[float, float, float]:
    """
    Updates superficial velocity u_s [m/s], mixture density rho [kg/m^3],
    and pressure gradient dP/dz [Pa/m] via Ergun momentum balance.
    """
    Z, rho = peng_robinson_compressibility(y_ret, T_K, P_Pa)
    
    # Dynamic superficial velocity
    # u_s = (F_total * Z * R * T) / (P * A_c)
    u_s = (F_ret_total * Z * R_GAS * T_K) / (P_Pa * A_c)
    
    # Dynamic viscosity
    mu = compute_mixture_viscosity(y_ret, T_K)
    
    # Ergun Equation
    # dP/dz = - [ 150 * mu * (1-eps)^2 / (d_p^2 * eps^3) * u_s + 1.75 * rho * (1-eps) / (d_p * eps^3) * u_s^2 ]
    term_viscous = 150.0 * mu * ((1.0 - eps)**2) / ((d_p**2) * (eps**3)) * u_s
    term_inertial = 1.75 * rho * (1.0 - eps) / (d_p * (eps**3)) * (u_s**2)
    dP_dz = -(term_viscous + term_inertial)
    
    return float(u_s), float(rho), float(dP_dz)
