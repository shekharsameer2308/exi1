"""
Machine Learning Surrogate Model Training, Multi-Model Benchmark, and Error Decomposition Suite.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def mean_absolute_percentage_error(y_true, y_pred, eps=1e-6):
    """Calculates safe Mean Absolute Percentage Error (MAPE) in %."""
    denom = np.maximum(np.abs(y_true), eps)
    return np.mean(np.abs((y_true - y_pred) / denom)) * 100.0


def train_surrogate_suite(
    data_path: str = "data/membrane_doe.csv",
    model_output_path: str = "surrogate_rf.joblib",
    results_dir: str = "results",
):
    print(f"=== Training ML Surrogate Benchmark on {data_path} ===")
    res_dir = Path(results_dir)
    res_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} validated simulation records.")

    features = ["T_in_K", "P_in_bar", "flow_mol_s", "h2_co2_ratio", "water_permeance"]
    # Check available features in CSV
    features = [f for f in features if f in df.columns]
    targets = ["co2_conversion", "meoh_yield", "meoh_selectivity", "h2o_removal_fraction"]
    targets = [t for t in targets if t in df.columns]

    X = df[features]
    y = df[targets]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )

    models = {
        "RandomForest": MultiOutputRegressor(RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)),
        "ExtraTrees": MultiOutputRegressor(ExtraTreesRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)),
        "GradientBoosting": MultiOutputRegressor(GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42)),
    }

    benchmark_rows = []
    trained_models = {}

    for name, model in models.items():
        print(f"\nTraining and evaluating: {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        trained_models[name] = model

        for i, target_name in enumerate(targets):
            y_t = y_test.iloc[:, i].values
            y_p = y_pred[:, i]
            
            r2 = r2_score(y_t, y_p)
            mae = mean_absolute_error(y_t, y_p)
            rmse = np.sqrt(mean_squared_error(y_t, y_p))
            mape = mean_absolute_percentage_error(y_t, y_p)

            benchmark_rows.append({
                "model": name,
                "target": target_name,
                "R2": r2,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE_percent": mape,
            })

    df_metrics = pd.DataFrame(benchmark_rows)
    df_metrics.to_csv(res_dir / "ml_metrics.csv", index=False)
    print("\n=== Model Evaluation Metrics Benchmark ===")
    print(df_metrics.to_string(index=False))

    # Best model selection (Random Forest / Extra Trees)
    best_model_name = "ExtraTrees" if df_metrics[df_metrics["model"]=="ExtraTrees"]["R2"].mean() > df_metrics[df_metrics["model"]=="RandomForest"]["R2"].mean() else "RandomForest"
    best_model = trained_models[best_model_name]

    # Save predictions & residuals for parity plots
    test_preds = best_model.predict(X_test)
    df_preds = pd.DataFrame(X_test.copy(), columns=features)
    for i, target_name in enumerate(targets):
        df_preds[f"actual_{target_name}"] = y_test.iloc[:, i].values
        df_preds[f"pred_{target_name}"] = test_preds[:, i]
        df_preds[f"residual_{target_name}"] = y_test.iloc[:, i].values - test_preds[:, i]

    df_preds.to_csv(res_dir / "ml_predictions.csv", index=False)

    # Serialize best surrogate
    joblib.dump(best_model, model_output_path)
    # Also save to results/
    joblib.dump(best_model, res_dir / "best_surrogate.joblib")
    print(f"\nBest surrogate ({best_model_name}) serialized to {model_output_path}")


if __name__ == "__main__":
    train_surrogate_suite()
