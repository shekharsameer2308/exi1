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
Core physics and kinetic parameters derived from:
Hauth et al. (2025). Design parameter optimization of a membrane reactor for methanol synthesis using a sophisticated CFD model. Energy Advances, 4, 565-577.
"""

import numpy as np

from core.thermodynamics import R_GAS, get_equilibrium_constants


def calculate_mignard_pritchard_rates(
    p_bar: np.ndarray,
    T_K: float,
    catalyst_activity: float = 1.0,
) -> tuple[float, float, dict[str, float]]:
    """
    Computes reaction rates r_MeOH and r_RWGS in mol / (kg_cat * s).

    Parameters
    ----------
    p_bar : np.ndarray
        Array of partial pressures [p_CO2, p_H2, p_CH3OH, p_H2O, p_CO] in bar.
    T_K : float
        Absolute temperature in Kelvin.
    catalyst_activity : float
        Activity scale factor.
    """
    p = np.maximum(p_bar[:5], 1e-12)
    p_co2, p_h2, p_meoh, p_h2o, p_co = p[0], p[1], p[2], p[3], p[4]

    RT = R_GAS * T_K

    # Kinetic parameters (Hauth et al. 2025 Table 2)
    k1 = 1.07 * np.exp(40000.0 / RT)
    k2 = 1.22e10 * np.exp(-98084.0 / RT)

    K_H2O = 6.62e-11 * np.exp(124119.0 / RT)
    K_H2_sqrt = 0.499 * np.exp(17197.0 / RT)
    K_H2O_H2 = 3453.38

    Keq1, Keq2 = get_equilibrium_constants(T_K)

    # Adsorption denominator
    denom = (
        1.0
        + (K_H2O_H2 * p_h2o / max(p_h2, 1e-4))
        + K_H2_sqrt * np.sqrt(max(p_h2, 1e-4))
        + K_H2O * p_h2o
    )

    # Driving forces
    drv1 = p_co2 * (p_h2**0.5) - (p_meoh * p_h2o / (Keq1 * (p_h2**2.5) + 1e-12))
    r_meoh = catalyst_activity * max((k1 * drv1) / (denom**3 + 1e-12), 0.0)

    drv2 = p_co2 - (p_h2o * p_co / (Keq2 * p_h2 + 1e-12))
    r_rwgs = catalyst_activity * (k2 * drv2) / (denom + 1e-12)

    info = {
        "driving_force_meoh": float(drv1),
        "driving_force_rwgs": float(drv2),
        "Keq1": Keq1,
        "Keq2": Keq2,
        "p_h2o_bar": float(p_h2o),
    }
    return float(r_meoh), float(r_rwgs), info


def check_catalyst_stability(
    p_h2o_bar: float,
    P_total_bar: float,
    min_fraction: float = 0.015,
) -> tuple[bool, float, str]:
    """
    Checks that p_H2O >= 0.015 * P_total to prevent over-reduction to alpha-CuZn brass.
    """
    threshold = min_fraction * P_total_bar
    is_safe = p_h2o_bar >= threshold
    margin = p_h2o_bar - threshold
    status = "PRESERVED" if is_safe else "WARNING_DEACTIVATION_RISK"
    return is_safe, margin, status


def calculate_reaction_rates(p_bar: np.ndarray, T_K: float, **kwargs):
    """Alias for calculate_mignard_pritchard_rates."""
    return calculate_mignard_pritchard_rates(p_bar, T_K, **kwargs)


def check_catalyst_preservation(p_h2o_bar: float, P_total_bar: float, **kwargs):
    """Alias for check_catalyst_stability."""
    return check_catalyst_stability(p_h2o_bar, P_total_bar, **kwargs)
