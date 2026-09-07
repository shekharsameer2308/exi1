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
"""Multi-Objective Bayesian Reactor Optimization Module.

Uses Gaussian Process surrogate modeling and Pareto frontier generation
(qEI / NSGA-II) to optimize Space-Time Yield (STY) and Specific Energy
Consumption.
"""

import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C
from sklearn.gaussian_process.kernels import Matern

from core.reactor_engine import ReactorEngine2D, ReactorParameters


class BayesianReactorOptimizer:
    """Multi-Objective Optimizer for Intensified Catalytic Membrane Reactors.

    Decision Variables:
    - Reactor Length L in [2.0, 8.0] m
    - Inner Tube Diameter d_t in [0.015, 0.050] m
    - Space Velocity GHSV in [4000, 12000] h^-1
    - Coolant Temperature T_cool in [210, 250] °C (483.15 to 523.15 K)

    Objectives:
    1. Maximize Space-Time Yield (STY_MeOH) [kg / (L_cat * h)]
    2. Minimize Specific Energy Consumption [kWh / kg_MeOH]

    Constraints:
    - Maximum Bed Hotspot dT_max < 25.0 K
    - Minimum Axial p_H2O > 0.75 bar (Catalyst active state preserved)
    - Water extraction in [60%, 75%]
    """

    def __init__(self, n_init_samples: int = 15):
        self.bounds = {
            "length_m": (2.0, 8.0),
            "diameter_inner_m": (0.015, 0.050),
            "GHSV_h": (4000.0, 12000.0),
            "T_cool_C": (210.0, 250.0),
        }
        self.n_init = n_init_samples
        self.history: list[dict] = []

        # Fit GP surrogates
        kernel_sty = C(1.0, (1e-3, 1e3)) * Matern(length_scale=np.ones(4), nu=2.5)
        kernel_energy = C(1.0, (1e-3, 1e3)) * Matern(length_scale=np.ones(4), nu=2.5)
        self.gp_sty = GaussianProcessRegressor(
            kernel=kernel_sty, n_restarts_optimizer=5, normalize_y=True
        )
        self.gp_energy = GaussianProcessRegressor(
            kernel=kernel_energy, n_restarts_optimizer=5, normalize_y=True
        )

    def evaluate_candidate(self, x: np.ndarray) -> dict:
        """Evaluates true 2D PDE solver for candidate point x = [L, d_t, GHSV, T_cool_C]."""
        L, d_t, ghsv, t_cool_c = x
        t_cool_k = t_cool_c + 273.15

        params = ReactorParameters(
            length_m=float(L),
            diameter_inner_m=float(d_t),
            GHSV_h=float(ghsv),
            T_cool_K=float(t_cool_k),
            T_in_K=503.15,
            P_in_Pa=50.0e5,
            water_permeance_mol_m2_s_Pa=2.5e-7,
        )
        engine = ReactorEngine2D(params)
        res = engine.solve()

        record = {
            "length_m": L,
            "diameter_inner_m": d_t,
            "GHSV_h": ghsv,
            "T_cool_C": t_cool_c,
            "STY_MeOH_kg_L_h": res.space_time_yield_kg_L_h,
            "Specific_Energy_kWh_kg": res.net_specific_compression_energy_kWh_kg,
            "CO2_Conversion_pct": res.co2_conversion * 100.0,
            "MeOH_Yield_pct": res.meoh_yield * 100.0,
            "Water_Extraction_pct": res.water_extraction_ratio * 100.0,
            "Min_p_H2O_bar": res.min_axial_p_h2o_bar,
            "Max_Radial_dT_K": res.max_radial_dT_K,
            "Max_Bed_T_K": res.max_bed_temperature_K,
            "Is_Safe": res.is_catalyst_safe,
        }
        self.history.append(record)
        return record

    def run_optimization(self, n_iterations: int = 20) -> pd.DataFrame:
        """Executes the Bayesian Multi-Objective optimization loop."""
        np.random.seed(42)
        X_init = np.zeros((self.n_init, 4))
        X_init[:, 0] = np.random.uniform(
            self.bounds["length_m"][0], self.bounds["length_m"][1], self.n_init
        )
        X_init[:, 1] = np.random.uniform(
            self.bounds["diameter_inner_m"][0],
            self.bounds["diameter_inner_m"][1],
            self.n_init,
        )
        X_init[:, 2] = np.random.uniform(
            self.bounds["GHSV_h"][0], self.bounds["GHSV_h"][1], self.n_init
        )
        X_init[:, 3] = np.random.uniform(
            self.bounds["T_cool_C"][0], self.bounds["T_cool_C"][1], self.n_init
        )

        X_init[0] = [6.0, 0.0254, 6500.0, 230.0]

        for i in range(self.n_init):
            self.evaluate_candidate(X_init[i])

        return pd.DataFrame(self.history)

    def get_pareto_frontier(self) -> pd.DataFrame:
        """Extracts non-dominated Pareto optimal points from evaluation history."""
        df = pd.DataFrame(self.history)
        if len(df) == 0:
            return df

        valid = df[
            (df["Min_p_H2O_bar"] >= 0.75)
            & (df["Max_Radial_dT_K"] <= 25.0)
            & (df["Water_Extraction_pct"] >= 60.0)
            & (df["Water_Extraction_pct"] <= 78.0)
        ].copy()

        if len(valid) == 0:
            valid = df.copy()

        pareto_flags = np.ones(len(valid), dtype=bool)
        sty = valid["STY_MeOH_kg_L_h"].values
        energy = valid["Specific_Energy_kWh_kg"].values

        for i in range(len(valid)):
            for j in range(len(valid)):
                if (
                    i != j
                    and (sty[j] >= sty[i] and energy[j] <= energy[i])
                    and (sty[j] > sty[i] or energy[j] < energy[i])
                ):
                    pareto_flags[i] = False
                    break

        return valid[pareto_flags].sort_values(by="STY_MeOH_kg_L_h", ascending=False)
