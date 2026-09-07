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

from core.solver_2d import AnnularReactor2DSolver, ReactorConfig


def test_cfd_reproduction():
    cfg_tr = ReactorConfig(is_membrane=False)
    res_tr = AnnularReactor2DSolver(cfg_tr).solve()

    cfg_mr = ReactorConfig(is_membrane=True)
    res_mr = AnnularReactor2DSolver(cfg_mr).solve()

    assert res_mr.co2_conversion_pct > res_tr.co2_conversion_pct
    assert res_mr.meoh_yield_pct > res_tr.meoh_yield_pct
    assert res_mr.retentate_exit_p_h2o_bar > 1.0
    assert res_mr.carbon_balance_error < 0.05
