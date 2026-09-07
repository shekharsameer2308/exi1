import pytest
import numpy as np
from core.maxwell_stefan import compute_maxwell_stefan_flux

def test_flux_non_negative():
    p_ret = np.array([5.0e5, 1.0e5, 70.0e5])
    p_perm = np.array([0.05e5, 0.01e5, 0.02e5])
    J = compute_maxwell_stefan_flux(p_ret, p_perm)
    assert np.all(J >= 0.0)
    assert J[0] > J[1]  # Water flux higher than methanol
