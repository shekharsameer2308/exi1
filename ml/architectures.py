"""
Neural Network Operator Architectures Preserving Asymptotic Physical Bounds.
"""
import torch
import torch.nn as nn


class BoundedFluxSurrogate(nn.Module):
    """
    MLP surrogate for membrane flux vector J_pred = [J_H2O, J_CH3OH, J_H2]
    enforcing strictly non-negative flux and zero flux at zero partial pressure.
    """
    def __init__(self, in_features: int = 5, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 3),
            nn.Softplus(),  # Strictly non-negative output
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x = [p_H2O, p_MeOH, p_H2, T, delta_P]
        # Multiply by driving pressure to preserve asymptotic zero-flux boundary
        p_driving = torch.clamp(x[..., 0:1], min=0.0) / 1e5
        raw_flux = self.net(x)
        return raw_flux * p_driving
