#
# Copyright 2026 Membrane-Reactor-SciML Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Hybrid SciML Grey-Box Neural ODE Flux Surrogate.
Couples mechanistic convection-dispersion and catalytic reaction terms
with a learned neural surrogate for the Maxwell-Stefan matrix inversion.
"""

import numpy as np
import torch
from torch import nn

from core.thermodynamics import R_GAS
from ml.architectures import BoundedFluxSurrogate


class SciMLReactorODE(nn.Module):
    """
    Solves: dC/dz = f_physics(C, T) - a_m * NN_phi(p, T, delta_p)
    """

    def __init__(
        self,
        surrogate: BoundedFluxSurrogate,
        a_m: float = 133.33,
        rho_bed: float = 1150.0,
    ):
        super().__init__()
        self.surrogate = surrogate
        self.a_m = a_m
        self.rho_bed = rho_bed
        self.T_op = 523.15
        self.P_ret = 100.0e5

    def forward(self, z: torch.Tensor, F: torch.Tensor) -> torch.Tensor:
        orig_dim = F.dim()
        if orig_dim == 1:
            F = F.unsqueeze(0)

        F_safe = torch.clamp(F, min=1e-12)
        F_tot = torch.sum(F_safe, dim=-1, keepdim=True)
        p_Pa = (F_safe / F_tot) * self.P_ret
        p_bar = p_Pa / 1.0e5

        # Catalytic kinetics (Mignard & Pritchard)
        RT = R_GAS * self.T_op
        k1 = 1.07 * np.exp(40000.0 / RT)
        k2 = 1.22e10 * np.exp(-98084.0 / RT)
        K_H2O = 6.62e-11 * np.exp(124119.0 / RT)
        K_H2_sqrt = 0.499 * np.exp(17197.0 / RT)
        K_H2O_H2 = 3453.38
        Keq1 = 10.0 ** (3066.0 / self.T_op - 10.592)
        Keq2 = 10.0 ** (-2073.0 / self.T_op + 2.029)

        denom = (
            1.0
            + (K_H2O_H2 * p_bar[:, 3] / torch.clamp(p_bar[:, 1], min=1e-4))
            + K_H2_sqrt * torch.sqrt(torch.clamp(p_bar[:, 1], min=1e-4))
            + K_H2O * p_bar[:, 3]
        )

        drv1 = p_bar[:, 0] * torch.sqrt(torch.clamp(p_bar[:, 1], min=1e-4)) - (
            p_bar[:, 3] * p_bar[:, 2] / (Keq1 * (p_bar[:, 1] ** 2.5) + 1e-12)
        )
        r_meoh = torch.clamp((k1 * drv1) / (denom**3 + 1e-12), min=0.0)

        drv2 = p_bar[:, 0] - (p_bar[:, 3] * p_bar[:, 4] / (Keq2 * p_bar[:, 1] + 1e-12))
        r_rwgs = (k2 * drv2) / (denom + 1e-12)

        # Net generation
        R_co2 = self.rho_bed * (-r_meoh - r_rwgs)
        R_h2 = self.rho_bed * (-3.0 * r_meoh - r_rwgs)
        R_meoh = self.rho_bed * (r_meoh)
        R_h2o = self.rho_bed * (r_meoh + r_rwgs)
        R_co = self.rho_bed * (r_rwgs)

        # Annular area
        d_w = 0.020
        d_m = 0.010
        A_c = (np.pi / 4.0) * (d_w**2 - d_m**2)

        dF_co2 = A_c * R_co2
        dF_h2 = A_c * R_h2
        dF_meoh = A_c * R_meoh
        dF_h2o = A_c * R_h2o
        dF_co = A_c * R_co

        # Neural flux bypass
        x_in = torch.stack(
            [
                p_Pa[:, 3],  # H2O
                p_Pa[:, 2],  # MeOH
                p_Pa[:, 1],  # H2
                self.T_op * torch.ones_like(p_Pa[:, 0]),
                99.0e5 * torch.ones_like(p_Pa[:, 0]),
            ],
            dim=-1,
        )

        J_pred = self.surrogate(x_in)

        dF_h2o = dF_h2o - self.a_m * A_c * J_pred[:, 0]
        dF_meoh = dF_meoh - self.a_m * A_c * J_pred[:, 1]
        dF_h2 = dF_h2 - self.a_m * A_c * J_pred[:, 2]

        dFdz = torch.stack([dF_co2, dF_h2, dF_meoh, dF_h2o, dF_co], dim=-1)

        if orig_dim == 1:
            return dFdz.squeeze(0)
        return dFdz
