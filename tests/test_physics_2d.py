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
Test suite for 2D Heterogeneous Catalytic Membrane Reactor (CMR) Physics & Transport.
"""
import numpy as np

from core.kinetics import check_catalyst_preservation
from core.reactor_engine import ReactorEngine2D, ReactorParameters
from core.transport_2d import (
    update_dynamic_ergun,
)


def test_catalyst_preservation_boundary():
    """Verify that water partial pressure boundary prevents active Cu+ reduction."""
    is_safe, margin, status = check_catalyst_preservation(
        0.86, 50.0, min_fraction=0.015
    )
    assert is_safe is True
    assert margin > 0.0
    assert status == "PRESERVED"

    is_safe_viol, margin_viol, status_viol = check_catalyst_preservation(
        0.60, 50.0, min_fraction=0.015
    )
    assert is_safe_viol is False
    assert margin_viol < 0.0
    assert "WARNING" in status_viol


def test_ergun_dynamic_molar_contraction():
    """Verify that superficial velocity updates dynamically with molar contraction."""
    y_in = np.array([0.2475, 0.7425, 0.0, 0.0, 0.0, 0.01])
    u_s, rho, dP_dz = update_dynamic_ergun(
        F_ret_total=0.10,
        y_ret=y_in,
        T_K=503.15,
        P_Pa=50e5,
        A_c=5.067e-4,
    )
    assert u_s > 0.0
    assert rho > 0.0
    assert dP_dz < 0.0


def test_2d_reactor_convergence():
    """Verify that 2D PDE solver converges and produces meaningful outputs."""
    params = ReactorParameters(
        length_m=3.0,
        diameter_inner_m=0.0254,
        GHSV_h=6500.0,
        T_in_K=503.15,
        P_in_Pa=50.0e5,
        water_permeance_mol_m2_s_Pa=2.5e-7,
        n_radial_nodes=5,
        n_axial_eval_points=50,
    )
    engine = ReactorEngine2D(params)
    res = engine.solve()
    assert res.co2_conversion > 0.0
    assert res.meoh_yield > 0.0
    assert res.water_extraction_ratio >= 0.0
