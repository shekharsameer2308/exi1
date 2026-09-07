"""
Test suite for 2D Heterogeneous Catalytic Membrane Reactor (CMR) Physics & Transport.
"""
import pytest
import numpy as np
from core.thermodynamics import get_reaction_enthalpies, get_equilibrium_constants, peng_robinson_compressibility
from core.kinetics import calculate_reaction_rates, check_catalyst_preservation
from core.transport_2d import compute_radial_dispersion, compute_effective_radial_conductivity, update_dynamic_ergun
from core.reactor_engine import ReactorParameters, ReactorEngine2D


def test_catalyst_preservation_boundary():
    """Verify that water partial pressure boundary prevents active Cu+ reduction."""
    # At 50 bar, 1.5% is 0.75 bar
    is_safe, margin, status = check_catalyst_preservation(0.86, 50.0, min_water_fraction=0.015)
    assert is_safe is True
    assert margin > 0.0
    assert status == "PRESERVED"
    
    # Boundary violation
    is_safe_viol, margin_viol, status_viol = check_catalyst_preservation(0.60, 50.0, min_water_fraction=0.015)
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
    assert dP_dz < 0.0  # Pressure drop must be negative


def test_2d_reactor_convergence():
    """Verify that 2D PDE solver converges and adheres to conservation constraints."""
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
    assert res.carbon_balance_error < 0.05
