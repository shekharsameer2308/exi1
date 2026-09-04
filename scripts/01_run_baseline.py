"""
Script to execute and archive baseline reactor performance, DOE dataset, and surrogate metrics.
"""
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import MembraneReactor1D, ODENonConvergenceError


def run_baseline():
    print("=== RUNNING BASELINE MODEL AUDIT & SIMULATION ===")
    baseline_dir = Path("results/baseline")
    baseline_dir.mkdir(parents=True, exist_ok=True)

    # 1. Single baseline simulation
    t0 = time.time()
    reactor = MembraneReactor1D(length=1.0, diameter=0.02)
    res = reactor.simulate(
        T_in=493.15,
        P_in=50.0,
        flow_in=0.015,
        h2_co2_ratio=3.0,
        water_permeance=1e-7,
    )
    runtime = time.time() - t0

    baseline_metrics = {
        "operating_conditions": {
            "T_in_K": 493.15,
            "P_in_bar": 50.0,
            "flow_mol_s": 0.015,
            "h2_co2_ratio": 3.0,
            "water_permeance": 1e-7,
            "reactor_length_m": 1.0,
            "reactor_diameter_m": 0.02,
        },
        "results": {
            "co2_conversion": res["co2_conversion"],
            "meoh_yield": res["meoh_yield"],
            "meoh_selectivity": res["meoh_yield"] / res["co2_conversion"] if res["co2_conversion"] > 0 else 0.0,
            "solver_success": True,
            "runtime_sec": runtime,
        },
    }

    import json
    with open(baseline_dir / "baseline_summary.json", "w") as f:
        json.dump(baseline_metrics, f, indent=4)

    print(f"Single simulation completed in {runtime*1000:.2f} ms")
    print(f"CO2 Conversion: {res['co2_conversion']*100:.2f}%")
    print(f"MeOH Yield:     {res['meoh_yield']*100:.2f}%")
    print(f"MeOH Selectivity: {baseline_metrics['results']['meoh_selectivity']*100:.2f}%")

    # 2. Baseline DOE generation
    print("\n--- Generating Baseline DOE (500 cases) ---")
    rng = np.random.default_rng(42)
    n_samples = 500
    T_in = rng.uniform(463.15, 523.15, n_samples)
    P_in = rng.uniform(30.0, 70.0, n_samples)
    h2_co2_ratio = rng.uniform(2.5, 4.0, n_samples)
    flow_in = rng.uniform(0.01, 0.03, n_samples)

    doe_results = []
    failures = 0
    t_doe_start = time.time()

    for i in range(n_samples):
        try:
            r = reactor.simulate(
                T_in=float(T_in[i]),
                P_in=float(P_in[i]),
                flow_in=float(flow_in[i]),
                h2_co2_ratio=float(h2_co2_ratio[i]),
            )
            doe_results.append({
                "T_in_K": float(T_in[i]),
                "P_in_bar": float(P_in[i]),
                "h2_co2_ratio": float(h2_co2_ratio[i]),
                "flow_mol_s": float(flow_in[i]),
                "co2_conversion": r["co2_conversion"],
                "meoh_yield": r["meoh_yield"],
            })
        except Exception as e:
            failures += 1

    doe_runtime = time.time() - t_doe_start
    df_doe = pd.DataFrame(doe_results)
    df_doe.to_csv(baseline_dir / "baseline_doe.csv", index=False)
    print(f"DOE generated in {doe_runtime:.2f} s. Success: {len(df_doe)}/{n_samples}, Failures: {failures}")

    # 3. Train Baseline Surrogate
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.multioutput import MultiOutputRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    X = df_doe[["T_in_K", "P_in_bar", "h2_co2_ratio", "flow_mol_s"]]
    y = df_doe[["co2_conversion", "meoh_yield"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    rf = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    r2_conv = r2_score(y_test.iloc[:, 0], y_pred[:, 0])
    r2_yield = r2_score(y_test.iloc[:, 1], y_pred[:, 1])
    mae_conv = mean_absolute_error(y_test.iloc[:, 0], y_pred[:, 0])
    mae_yield = mean_absolute_error(y_test.iloc[:, 1], y_pred[:, 1])
    overall_r2 = rf.score(X_test, y_test)

    ml_metrics = pd.DataFrame([
        {"target": "co2_conversion", "R2": r2_conv, "MAE": mae_conv, "RMSE": np.sqrt(mean_squared_error(y_test.iloc[:, 0], y_pred[:, 0]))},
        {"target": "meoh_yield", "R2": r2_yield, "MAE": mae_yield, "RMSE": np.sqrt(mean_squared_error(y_test.iloc[:, 1], y_pred[:, 1]))},
        {"target": "overall_multioutput", "R2": overall_r2, "MAE": (mae_conv+mae_yield)/2, "RMSE": 0.0},
    ])
    ml_metrics.to_csv(baseline_dir / "baseline_ml_metrics.csv", index=False)
    joblib.dump(rf, baseline_dir / "baseline_surrogate_rf.joblib")

    print("\n--- Baseline ML Metrics ---")
    print(ml_metrics.to_string(index=False))
    print("\nBaseline successfully recorded in results/baseline/")


if __name__ == "__main__":
    run_baseline()
