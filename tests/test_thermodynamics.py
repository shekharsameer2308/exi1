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
import numpy as np

from core.thermodynamics import (
    get_equilibrium_constants,
    get_pure_heat_capacity,
    peng_robinson_eos,
)


def test_heat_capacity_positivity():
    for sp in ["CO2", "H2", "CH3OH", "H2O", "CO"]:
        cp = get_pure_heat_capacity(sp, 523.15)
        assert cp > 0.0, f"Cp for {sp} must be positive."


def test_equilibrium_approach():
    Keq1, Keq2 = get_equilibrium_constants(523.15)
    assert Keq1 > 0.0
    assert Keq2 > 0.0


def test_peng_robinson_z():
    y = np.array([0.25, 0.75, 0.0, 0.0, 0.0])
    Z, rho = peng_robinson_eos(y, 523.15, 100.0e5)
    assert 0.8 < Z < 1.3
    assert rho > 0.0
