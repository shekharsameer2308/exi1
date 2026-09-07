"""
Grid Generator Extracting Training States from CFD Solutions.
Generates state-flux pairs for training the SciML Maxwell-Stefan neural surrogate.
"""
from typing import Tuple
import numpy as np
import torch
from core.maxwell_stefan import compute_maxwell_stefan_flux


def generate_ms_flux_dataset(n_samples: int = 500) -> Tuple[torch.Tensor, torch.Tensor]:
    """Generates synthetic CFD state-flux training dataset."""
    np.random.seed(42)
    # Pressures in Pa
    p_h2o = np.random.uniform(0.1e5, 10.0e5, n_samples)
    p_meoh = np.random.uniform(0.01e5, 5.0e5, n_samples)
    p_h2 = np.random.uniform(20.0e5, 80.0e5, n_samples)
    T = np.random.uniform(480.0, 540.0, n_samples)
    delta_p = np.random.uniform(50.0e5, 99.0e5, n_samples)
    
    X = np.stack([p_h2o, p_meoh, p_h2, T, delta_p], axis=-1)
    Y = np.zeros((n_samples, 3))
    
    for i in range(n_samples):
        p_ret = np.array([p_h2o[i], p_meoh[i], p_h2[i]])
        p_perm = np.array([0.05e5, 0.01e5, 0.02e5])
        Y[i] = compute_maxwell_stefan_flux(p_ret, p_perm, T_K=T[i])
        
    return torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32)
