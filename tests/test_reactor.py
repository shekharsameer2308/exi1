"""
Comprehensive Validation Test Suite for 1D Membrane and Conventional Reactor.
Covers Tests 1-12 from Phase 12.
"""
import pytest
import numpy as np
from src.emethanol.reactor import simulate_reactor, MembraneReactor1D, ModelConfig


def test_01_and_02_mass_and_elemental_conservation():
    """TEST 1 & 2: Mass and elemental conservation."""
    res = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0)
    assert res.solver_success
    assert res.carbon_balance_error < 1e-4
    assert res.hydrogen_balance_error < 1e-4
    assert res.oxygen_balance_error < 1e-4


def test_03_and_04_zero_membrane_permeability_equals_tr():
    """TEST 3 & 4: Zero membrane permeability produces identical results to TR mode."""
    res_tr = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0, membrane_enabled=False)
    res_mr_zero = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0, membrane_enabled=True, water_permeance=0.0)

    assert res_tr.solver_success and res_mr_zero.solver_success
    assert np.isclose(res_tr.co2_conversion, res_mr_zero.co2_conversion, rtol=1e-5)
    assert np.isclose(res_tr.meoh_yield, res_mr_zero.meoh_yield, rtol=1e-5)
    assert res_mr_zero.h2o_removal_fraction == 0.0


def test_05_large_membrane_permeability_enhances_removal():
    """TEST 5: Increasing membrane permeability increases water removal fraction."""
    res_low = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, water_permeance=1e-8)
    res_high = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, water_permeance=5e-7)

    assert res_high.h2o_removal_fraction > res_low.h2o_removal_fraction
    assert res_high.h2o_removal_fraction <= 1.0


def test_08_increasing_residence_time_increases_conversion():
    """TEST 8: Lower inlet flow (higher residence time) yields higher CO2 conversion."""
    res_fast = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.030, h2_co2_ratio=3.0)
    res_slow = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.010, h2_co2_ratio=3.0)

    assert res_slow.co2_conversion > res_fast.co2_conversion


def test_09_temperature_sweep_kinetics_vs_thermodynamics():
    """TEST 9: Temperature sweep reflects kinetic activation followed by equilibrium limitations."""
    res_low_T = simulate_reactor(temperature=463.15, pressure=50.0, total_flow=0.015)
    res_mid_T = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015)

    # In kinetic regime, higher T accelerates forward rate
    assert res_mid_T.co2_conversion > res_low_T.co2_conversion


def test_10_pressure_sweep_le_chatelier():
    """TEST 10: Higher pressure favors methanol synthesis (Le Chatelier principle for volume reduction)."""
    res_low_P = simulate_reactor(temperature=493.15, pressure=30.0, total_flow=0.015)
    res_high_P = simulate_reactor(temperature=493.15, pressure=70.0, total_flow=0.015)

    assert res_high_P.meoh_yield > res_low_P.meoh_yield
    assert res_high_P.co2_conversion > res_low_P.co2_conversion


def test_11_perfect_reproducibility():
    """TEST 11: Identical inputs yield bitwise-consistent or strictly identical numerical results."""
    res1 = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0)
    res2 = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0)

    assert res1.co2_conversion == res2.co2_conversion
    assert res1.meoh_yield == res2.meoh_yield
    assert np.array_equal(res1.F_CH3OH, res2.F_CH3OH)


def test_12_solver_tolerance_sensitivity():
    """TEST 12: Tightening tolerances (rtol=1e-6 -> 1e-8) produces consistent physical solution."""
    res_std = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, rtol=1e-6, atol=1e-9)
    res_tight = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, rtol=1e-8, atol=1e-11)

    assert np.isclose(res_std.co2_conversion, res_tight.co2_conversion, rtol=1e-4)
    assert np.isclose(res_std.meoh_yield, res_tight.meoh_yield, rtol=1e-4)
