import pytest
import numpy as np
from core.kinetics import calculate_mignard_pritchard_rates, check_catalyst_stability

def test_rate_laws():
    p_bar = np.array([25.0, 75.0, 0.0, 0.0, 0.0])
    r_m, r_w, info = calculate_mignard_pritchard_rates(p_bar, 523.15)
    assert r_m >= 0.0
    assert r_w >= 0.0

def test_catalyst_stability():
    is_safe, margin, _ = check_catalyst_stability(2.85, 100.0)
    assert is_safe is True
    assert margin > 0.0
