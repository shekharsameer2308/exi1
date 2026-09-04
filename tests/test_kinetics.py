"""
Unit tests for kinetic rate equations (VBF and Mignard-Pritchard).
"""
import pytest
import numpy as np
from src.emethanol.kinetics import calculate_rates
from src.emethanol.thermodynamics import get_equilibrium_constants


def test_positive_forward_rates_under_normal_feed():
    """Test 1: Rates should be strictly positive for unreacted syngas feed."""
    p_feed = np.array([10.0, 30.0, 0.0, 0.0, 0.0])  # 10 bar CO2, 30 bar H2
    T = 493.15  # 220 C
    
    r_meoh_vbf, r_rwgs_vbf = calculate_rates(p_feed, T, model="VBF")
    assert r_meoh_vbf > 0.0, f"Expected positive MeOH rate in VBF, got {r_meoh_vbf}"
    assert r_rwgs_vbf > 0.0, f"Expected positive RWGS rate in VBF, got {r_rwgs_vbf}"

    r_meoh_mp, r_rwgs_mp = calculate_rates(p_feed, T, model="MIGNARD_PRITCHARD")
    assert r_meoh_mp > 0.0, f"Expected positive MeOH rate in Mignard-Pritchard, got {r_meoh_mp}"
    assert r_rwgs_mp > 0.0, f"Expected positive RWGS rate in Mignard-Pritchard, got {r_rwgs_mp}"


def test_equilibrium_approach_zero_driving_force():
    """Test 2: Driving force approaches zero when products match equilibrium."""
    T = 500.0
    Keq1, Keq3 = get_equilibrium_constants(T, model="VBF")
    
    p_co2 = 5.0
    p_h2 = 15.0
    # At equilibrium for rxn 1: (p_meoh * p_h2o) = Keq1 * p_co2 * (p_h2^3)
    target_product = Keq1 * p_co2 * (p_h2 ** 3.0)
    p_meoh = np.sqrt(target_product)
    p_h2o = np.sqrt(target_product)
    p_co = 0.001
    
    p_eq = np.array([p_co2, p_h2, p_co, p_meoh, p_h2o])
    r_meoh, _ = calculate_rates(p_eq, T, model="VBF")
    
    # Rate should be negligible compared to forward rate
    assert abs(r_meoh) < 1e-4, f"Rate at equilibrium should be near zero, got {r_meoh}"


def test_kinetics_determinism_and_no_nans():
    """Test 3: Rate calculations are deterministic with no NaNs/Infs."""
    p_test = np.array([12.5, 37.5, 1.2, 2.5, 3.1])
    T = 513.15
    
    r1a, r2a = calculate_rates(p_test, T, model="VBF")
    r1b, r2b = calculate_rates(p_test, T, model="VBF")
    
    assert r1a == r1b and r2a == r2b, "Rates must be perfectly deterministic"
    assert not np.isnan(r1a) and not np.isnan(r2a), "Rates must not be NaN"
    assert not np.isinf(r1a) and not np.isinf(r2a), "Rates must not be Inf"


def test_invalid_temperature_handling():
    """Test 4: Non-positive temperatures must raise ValueError."""
    with pytest.raises(ValueError):
        calculate_rates(np.array([10.0, 30.0, 0, 0, 0]), T_K=-100.0)
    with pytest.raises(ValueError):
        calculate_rates(np.array([10.0, 30.0, 0, 0, 0]), T_K=0.0)
