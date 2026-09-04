"""
Script to execute multi-parameter 1D and 2D sweeps and sensitivity analysis.
"""
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import simulate_reactor


def run_parameter_sweeps():
    print("=== Executing Systematic Parameter Sweeps ===")
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Temperature Sweep (200 - 260 °C)
    temps = np.linspace(473.15, 533.15, 15)
    t_results = []
    for T in temps:
        res = simulate_reactor(temperature=float(T), pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0)
        t_results.append({
            "T_in_K": float(T),
            "T_in_C": float(T - 273.15),
            "co2_conversion": res.co2_conversion,
            "meoh_yield": res.meoh_yield,
            "meoh_selectivity": res.meoh_selectivity,
            "h2o_removal_fraction": res.h2o_removal_fraction,
            "outlet_temp_K": res.outlet_temperature,
            "max_temp_K": res.max_temperature,
        })
    df_temp = pd.DataFrame(t_results)
    df_temp.to_csv(out_dir / "sweep_temperature.csv", index=False)
    print("Saved sweep_temperature.csv")

    # 2. Pressure Sweep (20 - 80 bar)
    pressures = np.linspace(20.0, 80.0, 15)
    p_results = []
    for P in pressures:
        res = simulate_reactor(temperature=493.15, pressure=float(P), total_flow=0.015, h2_co2_ratio=3.0)
        p_results.append({
            "P_in_bar": float(P),
            "co2_conversion": res.co2_conversion,
            "meoh_yield": res.meoh_yield,
            "meoh_selectivity": res.meoh_selectivity,
            "h2o_removal_fraction": res.h2o_removal_fraction,
        })
    df_press = pd.DataFrame(p_results)
    df_press.to_csv(out_dir / "sweep_pressure.csv", index=False)
    print("Saved sweep_pressure.csv")

    # 3. Flow (GHSV) Sweep
    flows = np.linspace(0.008, 0.030, 15)
    f_results = []
    for f in flows:
        res = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=float(f), h2_co2_ratio=3.0)
        f_results.append({
            "flow_mol_s": float(f),
            "co2_conversion": res.co2_conversion,
            "meoh_yield": res.meoh_yield,
            "meoh_selectivity": res.meoh_selectivity,
            "h2o_removal_fraction": res.h2o_removal_fraction,
        })
    df_flow = pd.DataFrame(f_results)
    df_flow.to_csv(out_dir / "sweep_flow.csv", index=False)
    print("Saved sweep_flow.csv")

    # 4. Membrane Permeance Sweep (TR vs MR)
    perms = np.linspace(0.0, 3.0e-7, 15)
    perm_results = []
    for q in perms:
        res = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, water_permeance=float(q), membrane_enabled=(q > 0))
        perm_results.append({
            "water_permeance": float(q),
            "co2_conversion": res.co2_conversion,
            "meoh_yield": res.meoh_yield,
            "meoh_selectivity": res.meoh_selectivity,
            "h2o_removal_fraction": res.h2o_removal_fraction,
        })
    df_perm = pd.DataFrame(perm_results)
    df_perm.to_csv(out_dir / "sweep_membrane_permeance.csv", index=False)
    print("Saved sweep_membrane_permeance.csv")
    print("All parameter sweeps completed successfully.")


if __name__ == "__main__":
    run_parameter_sweeps()
