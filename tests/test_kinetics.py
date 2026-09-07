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

from core.kinetics import calculate_mignard_pritchard_rates, check_catalyst_stability


def test_rate_laws():
    p_bar = np.array([25.0, 75.0, 0.0, 0.0, 0.0])
    r_m, r_w, _info = calculate_mignard_pritchard_rates(p_bar, 523.15)
    assert r_m >= 0.0
    assert r_w >= 0.0


def test_catalyst_stability():
    is_safe, margin, _ = check_catalyst_stability(2.85, 100.0)
    assert is_safe is True
    assert margin > 0.0
