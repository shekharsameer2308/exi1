"""
Unit tests for elemental conservation (Carbon, Hydrogen, Oxygen).
"""
import pytest
import numpy as np
from src.emethanol.reactor import simulate_reactor


def test_elemental_conservation_membrane_reactor():
    """Test 1: C, H, and O atom balances must close within tight tolerance (< 1e-4) in MR."""
    res = simulate_reactor(
        temperature=493.15,
        pressure=50.0,
        total_flow=0.015,
        h2_co2_ratio=3.0,
        water_permeance=1.0e-7,
        membrane_enabled=True,
    )
    
    assert res.solver_success, "Simulation must succeed"
    assert res.carbon_balance_error < 1e-4, f"Carbon balance error too high: {res.carbon_balance_error}"
    assert res.hydrogen_balance_error < 1e-4, f"Hydrogen balance error too high: {res.hydrogen_balance_error}"
    assert res.oxygen_balance_error < 1e-4, f"Oxygen balance error too high: {res.oxygen_balance_error}"
    assert res.is_physically_valid, f"Validation failed: {res.validation_message}"


def test_elemental_conservation_conventional_reactor():
    """Test 2: C, H, and O atom balances must close in conventional reactor (TR)."""
    res = simulate_reactor(
        temperature=503.15,
        pressure=60.0,
        total_flow=0.02,
        h2_co2_ratio=3.5,
        membrane_enabled=False,
    )
    
    assert res.solver_success, "TR simulation must succeed"
    assert res.carbon_balance_error < 1e-4, f"Carbon error: {res.carbon_balance_error}"
    assert res.hydrogen_balance_error < 1e-4, f"Hydrogen error: {res.hydrogen_balance_error}"
    assert res.oxygen_balance_error < 1e-4, f"Oxygen error: {res.oxygen_balance_error}"
