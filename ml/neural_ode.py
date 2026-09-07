"""
Grey-Box Neural Ordinary Differential Equation (Neural ODE) Layer.
Couples mechanistic mass & energy conservation balances with a learned
PyTorch neural network that captures non-ideal boundary slip,
membrane fouling, and catalyst deactivation.
"""
from typing import Dict, Tuple, Optional, List
import numpy as np
import torch
import torch.nn as nn
from torchdiffeq import odeint

from core.thermodynamics import R_GAS, SPECIES_IDX, N_SPECIES, MOLAR_MASSES


class ReactorNeuralCorrector(nn.Module):
    """
    Learns non-ideal boundary slip, membrane fouling factor f_foul(z, t),
    and catalyst active state preservation corrections.
    """
    def __init__(self, state_dim: int = 8, hidden_dim: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, state_dim),
        )
        # Bounded scaling parameter
        self.scale = nn.Parameter(torch.tensor(0.01))
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        # State: [F_co2, F_h2, F_co, F_meoh, F_h2o, F_n2, T, P]
        correction = self.net(state) * torch.sigmoid(self.scale)
        return correction


class GreyBoxODEFunction(nn.Module):
    """
    Hybrid Physics + Neural ODE Right-Hand-Side function:
    dy/dz = f_physics(y, z) + g(y) * NN_theta(y)
    """
    def __init__(self, corrector: ReactorNeuralCorrector, reactor_params: Dict):
        super().__init__()
        self.corrector = corrector
        self.params = reactor_params
        self.d_t = self.params.get("diameter_inner_m", 0.0254)
        self.A_c = np.pi * ((self.d_t / 2.0)**2)
        self.rho_b = self.params.get("rho_b_kg_m3", 1150.0)
        self.U_wall = self.params.get("U_wall", 450.0)
        self.T_cool = self.params.get("T_cool_K", 503.15)
        self.Q_h2o_0 = self.params.get("water_permeance", 2.5e-7)
        self.Ea_mem = self.params.get("permeance_Ea_kJ_mol", 12.0) * 1e3
        
    def forward(self, z: torch.Tensor, state: torch.Tensor) -> torch.Tensor:
        # state: shape (batch_size, 8) or (8,)
        orig_shape = state.shape
        if state.dim() == 1:
            state = state.unsqueeze(0)
            
        F = torch.clamp(state[:, 0:6], min=1e-12)
        T = torch.clamp(state[:, 6], min=300.0, max=800.0)
        P = torch.clamp(state[:, 7], min=1e5, max=100e5)
        
        F_tot = torch.sum(F, dim=-1, keepdim=True)
        y_mol = F / F_tot
        p_bar = y_mol * (P.unsqueeze(-1) / 1e5)
        
        # Mechanistic Kinetic Rates (VBF)
        RT = R_GAS * T
        k5a = 2.18e12 * torch.exp(-87500.0 / RT)
        k1_r = 1.22e6 * torch.exp(-94765.0 / RT)
        
        Keq1 = 10.0 ** (3066.0 / T - 10.592)
        Keq2 = 10.0 ** (-2073.0 / T + 2.029)
        
        K_H2O_KH2half = 6.62e-11 * torch.exp(124119.0 / RT)
        K_H2half = 0.499 * torch.exp(17197.0 / RT)
        K_H2O = 6.37e-9 * torch.exp(113700.0 / RT)
        
        denom = (
            1.0
            + K_H2O_KH2half * (p_bar[:, 4] / torch.sqrt(torch.clamp(p_bar[:, 1], min=1e-4)))
            + K_H2half * torch.sqrt(torch.clamp(p_bar[:, 1], min=1e-4))
            + K_H2O * p_bar[:, 4]
        )
        denom = torch.clamp(denom, min=1.0)
        
        df1 = 1.0 - (p_bar[:, 3] * p_bar[:, 4]) / (Keq1 * p_bar[:, 0] * (p_bar[:, 1]**3.0) + 1e-15)
        df2 = 1.0 - (p_bar[:, 2] * p_bar[:, 4]) / (Keq2 * p_bar[:, 0] * p_bar[:, 1] + 1e-15)
        
        k_act = 8.50
        r_meoh = k_act * 0.85 * (k5a * p_bar[:, 0] * p_bar[:, 1] * df1) / (denom**3.0)
        r_rwgs = k_act * 0.90 * (k1_r * p_bar[:, 0] * p_bar[:, 1] * df2) / denom
        
        r_meoh = torch.clamp(r_meoh, min=-50.0, max=50.0)
        r_rwgs = torch.clamp(r_rwgs, min=-50.0, max=50.0)
        
        # Membrane Water Permeation
        Q_mem = self.Q_h2o_0 * torch.exp(-(self.Ea_mem / R_GAS) * (1.0 / T - 1.0 / 503.15))
        p_perm_h2o_bar = 1.2 * 0.05
        dp_h2o_Pa = torch.clamp((p_bar[:, 4] - p_perm_h2o_bar) * 1e5, min=0.0)
        J_h2o = Q_mem * dp_h2o_Pa
        
        # Derivatives dF_i / dz
        dF_co2 = self.A_c * self.rho_b * (-r_meoh - r_rwgs) - (np.pi * self.d_t * J_h2o / 450.0)
        dF_h2 = self.A_c * self.rho_b * (-3.0 * r_meoh - r_rwgs) - (np.pi * self.d_t * J_h2o / 220.0)
        dF_co = self.A_c * self.rho_b * (r_rwgs)
        dF_meoh = self.A_c * self.rho_b * (r_meoh)
        dF_h2o = self.A_c * self.rho_b * (r_meoh + r_rwgs) - (np.pi * self.d_t * J_h2o)
        dF_n2 = torch.zeros_like(dF_co2)
        
        # Energy balance
        dH1 = -49.5e3
        dH2 = 41.2e3
        Q_rxn = self.A_c * self.rho_b * ((-dH1) * r_meoh + (-dH2) * r_rwgs)
        Q_cool = self.U_wall * np.pi * self.d_t * (T - self.T_cool)
        Q_des = np.pi * self.d_t * J_h2o * 45.0e3
        
        Cp_avg = 42.0  # J / (mol * K)
        dT = (Q_rxn - Q_cool - Q_des) / torch.clamp(F_tot.squeeze(-1) * Cp_avg, min=1e-2)
        dP = -450.0 * torch.ones_like(dT)  # Pa / m
        
        f_physics = torch.stack([dF_co2, dF_h2, dF_co, dF_meoh, dF_h2o, dF_n2, dT, dP], dim=-1)
        
        # Neural Corrector Term
        nn_correction = self.corrector(state)
        
        dydz = f_physics + nn_correction
        
        if len(orig_shape) == 1:
            return dydz.squeeze(0)
        return dydz


class GreyBoxNeuralODEReactor:
    """
    High-level Python Interface for training and evaluating the Grey-Box Neural ODE.
    """
    def __init__(self, reactor_params: Optional[Dict] = None):
        self.params = reactor_params or {
            "diameter_inner_m": 0.0254,
            "length_m": 6.0,
            "rho_b_kg_m3": 1150.0,
            "T_cool_K": 503.15,
            "water_permeance": 2.5e-7,
        }
        self.corrector = ReactorNeuralCorrector(state_dim=8, hidden_dim=32)
        self.ode_func = GreyBoxODEFunction(self.corrector, self.params)
        
    def predict(
        self,
        y0: np.ndarray,
        z_eval: np.ndarray,
    ) -> np.ndarray:
        """
        Integrates the Neural ODE along z coordinates.
        """
        self.corrector.eval()
        with torch.no_grad():
            y0_tensor = torch.tensor(y0, dtype=torch.float32)
            z_tensor = torch.tensor(z_eval, dtype=torch.float32)
            traj_tensor = odeint(self.ode_func, y0_tensor, z_tensor, method="rk4")
            return traj_tensor.cpu().numpy()
            
    def fit(self, training_trajectories: List[Tuple[np.ndarray, np.ndarray]], epochs: int = 50, lr: float = 1e-3):
        """Trains neural corrector on observed experimental/CFD trajectories."""
        optimizer = torch.optim.Adam(self.corrector.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        self.corrector.train()
        for epoch in range(epochs):
            total_loss = 0.0
            for z_obs, y_obs in training_trajectories:
                optimizer.zero_grad()
                y0_t = torch.tensor(y_obs[0], dtype=torch.float32)
                z_t = torch.tensor(z_obs, dtype=torch.float32)
                y_target = torch.tensor(y_obs, dtype=torch.float32)
                
                y_pred = odeint(self.ode_func, y0_t, z_t, method="rk4")
                loss = criterion(y_pred, y_target)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                
        self.corrector.eval()
        return total_loss / max(len(training_trajectories), 1)
