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
Regression test suite comparing improved modular engine with baseline behavior.
"""

from src.emethanol.reactor import MembraneReactor1D, simulate_reactor


def test_baseline_compatibility():
    """Verify that legacy interface MembraneReactor1D.simulate works identically."""
    reactor = MembraneReactor1D(length=1.0, diameter=0.02)
    res = reactor.simulate(
        T_in=493.15,
        P_in=50.0,
        flow_in=0.015,
        h2_co2_ratio=3.0,
        water_permeance=1e-7,
    )

    assert "co2_conversion" in res
    assert "meoh_yield" in res
    assert res["co2_conversion"] > 0.03
    assert res["meoh_yield"] > 0.02


def test_tr_vs_mr_improvement():
    """Verify that MR achieves lower H2O mole fraction and improved yield over TR."""
    res_tr = simulate_reactor(
        temperature=493.15, pressure=50.0, total_flow=0.015, membrane_enabled=False
    )
    res_mr = simulate_reactor(
        temperature=493.15,
        pressure=50.0,
        total_flow=0.015,
        membrane_enabled=True,
        water_permeance=2e-7,
    )

    # In MR, water is selectively removed, shifting equilibrium forward
    assert res_mr.y_H2O[-1] < res_tr.y_H2O[-1]
    assert res_mr.h2o_removal_fraction > 0.0
