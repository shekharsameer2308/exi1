import pytest
import numpy as np
from core.thermodynamics import get_pure_heat_capacity, get_reaction_enthalpies, get_equilibrium_constants, peng_robinson_eos

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
