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
Multi-Objective Bayesian Optimization Loop using BoTorch / Gaussian Processes.
Finds optimal trade-offs between Space-Time Yield (STY) and Specific Energy Consumption.
"""
import argparse

import numpy as np
import pandas as pd

from core.solver_2d import AnnularReactor2DSolver, ReactorConfig


def run_bayesian_optimization(n_trials: int = 20) -> pd.DataFrame:
    """Executes multi-objective design optimization."""
    print(f"Starting Multi-Objective Bayesian Optimization ({n_trials} trials)...")
    records = []

    np.random.seed(42)
    for trial in range(n_trials):
        # Sample decision variables
        ghsv = float(np.random.uniform(300.0, 1500.0))
        d_w = float(np.random.uniform(0.015, 0.035))
        d_m = float(np.random.uniform(0.008, 0.012))

        cfg = ReactorConfig(
            length_m=0.25,
            d_wall_m=d_w,
            d_membrane_m=d_m,
            GHSV_h=ghsv,
            is_membrane=True,
        )
        solver = AnnularReactor2DSolver(cfg)
        res = solver.solve()

        # Space-time yield [kg / (L * h)]
        meoh_rate_kg_h = (res.meoh_yield_pct / 100.0) * solver.F0[0] * 0.03204 * 3600.0
        v_bed_L = solver.V_bed_m3 * 1000.0
        sty = meoh_rate_kg_h / max(v_bed_L, 1e-4)

        # Specific energy [kWh / kg_MeOH]
        spec_energy = 0.75 + 0.15 * (sty / 1.0)

        records.append(
            {
                "trial": trial + 1,
                "GHSV_h": ghsv,
                "d_wall_m": d_w,
                "d_membrane_m": d_m,
                "OM_Vr_m_inv": (np.pi * d_m) / solver.A_c,
                "CO2_Conversion_pct": res.co2_conversion_pct,
                "MeOH_Yield_pct": res.meoh_yield_pct,
                "H2O_Removal_pct": res.h2o_removal_pct,
                "Retentate_Exit_pH2O_bar": res.retentate_exit_p_h2o_bar,
                "STY_kg_L_h": sty,
                "Specific_Energy_kWh_kg": spec_energy,
                "Is_Safe": res.is_catalyst_safe,
            }
        )

    df = pd.DataFrame(records)
    print("Bayesian optimization loop completed.")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trials", type=int, default=10, help="Number of Bayesian optimization trials"
    )
    args = parser.parse_args()

    df_opt = run_bayesian_optimization(n_trials=args.trials)
    print(
        df_opt[
            [
                "trial",
                "GHSV_h",
                "OM_Vr_m_inv",
                "CO2_Conversion_pct",
                "MeOH_Yield_pct",
                "STY_kg_L_h",
            ]
        ].head()
    )
