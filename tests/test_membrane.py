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
Unit tests for membrane transport models (LDF and Maxwell-Stefan).
"""
import numpy as np

from src.emethanol.membrane import calculate_membrane_flux


def test_zero_driving_force_zero_flux():
    """Test 1: When reaction and sweep pressures match, flux should be identically zero."""
    p_equal = np.array([5.0, 15.0, 1.0, 2.0, 3.0])
    fluxes_ldf = calculate_membrane_flux(p_equal, p_equal, T_K=500.0, model="LDF")
    assert np.all(
        fluxes_ldf == 0.0
    ), f"Expected 0 flux for equal pressures, got {fluxes_ldf}"

    fluxes_ms = calculate_membrane_flux(
        p_equal, p_equal, T_K=500.0, model="MAXWELL_STEFAN"
    )
    assert np.all(
        fluxes_ms == 0.0
    ), f"Expected 0 flux for equal pressures, got {fluxes_ms}"


def test_positive_water_flux_with_driving_force():
    """Test 2: Water flux is positive and dominant when reaction p_H2O > sweep p_H2O."""
    p_rxn = np.array([10.0, 30.0, 1.0, 2.0, 5.0])
    p_swp = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

    fluxes_ldf = calculate_membrane_flux(
        p_rxn, p_swp, T_K=500.0, model="LDF", permeance_h2o_base=1e-7
    )
    assert fluxes_ldf[4] > 0.0, "H2O flux must be positive"
    # Selectivity check: H2O flux must exceed CO2/H2 leakage
    assert (
        fluxes_ldf[4] > fluxes_ldf[0] * 100.0
    ), "H2O must have high selectivity over CO2"

    fluxes_ms = calculate_membrane_flux(
        p_rxn, p_swp, T_K=500.0, model="MAXWELL_STEFAN", permeance_h2o_base=1e-7
    )
    assert fluxes_ms[4] > 0.0, "H2O flux in MS must be positive"


def test_no_negative_fluxes_reverse_driving_force():
    """Test 3: Sweep pressure higher than reaction pressure must not produce negative reaction flux."""
    p_rxn = np.array([10.0, 30.0, 1.0, 2.0, 1.0])
    p_swp = np.array([0.0, 0.0, 0.0, 0.0, 5.0])  # Higher H2O in sweep

    fluxes = calculate_membrane_flux(p_rxn, p_swp, T_K=500.0, model="LDF")
    assert np.all(fluxes >= 0.0), "Fluxes must remain non-negative"
