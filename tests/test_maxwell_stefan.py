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

from core.maxwell_stefan import compute_maxwell_stefan_flux


def test_flux_non_negative():
    p_ret = np.array([5.0e5, 1.0e5, 70.0e5])
    p_perm = np.array([0.05e5, 0.01e5, 0.02e5])
    J = compute_maxwell_stefan_flux(p_ret, p_perm)
    assert np.all(J >= 0.0)
    assert J[0] > J[1]  # Water flux higher than methanol
