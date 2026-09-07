#
# Copyright 2026 Membrane-Reactor-SciML Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Coupled Maxwell-Stefan permeation matrix parameters derived from:
Hauth et al. (2025). Design parameter optimization of a membrane reactor for methanol synthesis using a sophisticated CFD model. Energy Advances, 4, 565-577.
"""

import numpy as np

from core.thermodynamics import R_GAS

# Baseline parameters (Hauth et al. 2025 Table 3)
B0 = np.array([1.64e-12, 5.64e-15, 3.22e-9])  # Pa^-1
DH_ADS = np.array([-40.0e3, -65.0e3, -5.9e3])  # J / mol
Q_SAT = np.array([15.0, 6.2, 7.08e-4])  # mol / kg_memb
D0 = np.array([7.08e-4, 1.03e-7, 1.70e-8])  # m^2 / s
E_A = np.array([36.0e3, 17.0e3, 1.9e3])  # J / mol
D_H2O_CH3OH = 3.0e-9  # m^2 / s
RHO_MEMB = 1900.0  # kg / m^3
T_MEMB_DEFAULT = 0.0015  # 1.5 mm


def compute_maxwell_stefan_flux(
    p_ret_Pa: np.ndarray,
    p_perm_Pa: np.ndarray,
    T_K: float = 523.15,
    t_m: float = T_MEMB_DEFAULT,
    rho_m: float = RHO_MEMB,
) -> np.ndarray:
    """
    Computes coupled ternary flux vector J = [J_H2O, J_CH3OH, J_H2] in mol / (m^2 * s).

    Parameters
    ----------
    p_ret_Pa : np.ndarray of shape (3,)
        Retentate interface partial pressures [p_H2O, p_CH3OH, p_H2] in Pa.
    p_perm_Pa : np.ndarray of shape (3,)
        Permeate interface partial pressures [p_H2O, p_CH3OH, p_H2] in Pa.
    T_K : float
        Membrane temperature in Kelvin.
    t_m : float
        Membrane thickness in meters.
    rho_m : float
        Membrane density in kg / m^3.
    """
    p_ret = np.maximum(p_ret_Pa, 0.0)
    p_perm = np.maximum(p_perm_Pa, 0.0)

    RT = R_GAS * T_K
    b = B0 * np.exp(-DH_ADS / RT)
    D_pure = D0 * np.exp(-E_A / RT)

    denom_ret = 1.0 + np.sum(b * p_ret)
    theta_ret = (b * p_ret) / max(denom_ret, 1e-12)

    denom_perm = 1.0 + np.sum(b * p_perm)
    theta_perm = (b * p_perm) / max(denom_perm, 1e-12)

    theta = np.maximum(0.5 * (theta_ret + theta_perm), 1e-8)
    theta_v = max(1.0 - np.sum(theta), 1e-6)

    Gamma = np.eye(3) + (theta[:, np.newaxis] / theta_v)

    B = np.zeros((3, 3))
    D_12 = D_H2O_CH3OH
    D_13 = np.sqrt(D_pure[0] * D_pure[2])
    D_23 = np.sqrt(D_pure[1] * D_pure[2])

    B[0, 0] = (1.0 / D_pure[0]) + (theta[1] / D_12) + (theta[2] / D_13)
    B[0, 1] = -theta[0] / D_12
    B[0, 2] = -theta[0] / D_13

    B[1, 0] = -theta[1] / D_12
    B[1, 1] = (1.0 / D_pure[1]) + (theta[0] / D_12) + (theta[2] / D_23)
    B[1, 2] = -theta[1] / D_23

    B[2, 0] = -theta[2] / D_13
    B[2, 1] = -theta[2] / D_23
    B[2, 2] = (1.0 / D_pure[2]) + (theta[0] / D_13) + (theta[1] / D_23)

    dtheta_dr = (theta_perm - theta_ret) / max(t_m, 1e-6)

    B_inv = np.linalg.inv(B)
    J = -rho_m * Q_SAT * (B_inv @ Gamma @ dtheta_dr)

    return np.maximum(J, 0.0)
