"""
train_dme_surrogate.py
======================
Generates a Design of Experiments (DOE) dataset for direct CO2-to-DME membrane
reactors, trains multi-output machine learning surrogate models (RandomForest,
ExtraTrees, GradientBoosting), computes test evaluation metrics (R2, MAE, RMSE, MAPE),
feature importances, and parity diagnostic plots.
"""

import sys
from pathlib import Path
sys.path.insert(0, '.')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from dme_bundle_reactor import bundle_layout
from dme_membrane_reactor import run_dme_simulation


def mean_absolute_percentage_error(y_true, y_pred, eps=1e-6):
    denom = np.maximum(np.abs(y_true), eps)
    return np.mean(np.abs((y_true - y_pred) / denom)) * 100.0


def main():
    print("=== Step 1: Generating DOE Dataset for Direct CO2-to-DME CMR ===")
    np.random.seed(42)
    n_samples = 120

    # Sampling ranges
    T_samples = np.random.uniform(220.0, 270.0, n_samples)
    P_samples = np.random.uniform(30.0, 60.0, n_samples)
    dt_samples = np.random.uniform(3.0, 6.0, n_samples)
    mem_choices = ['NaA', 'LTA', 'CMSM']
    mem_samples = np.random.choice(mem_choices, n_samples)

    # Permeance mapping for feature vector
    perm_map = {'NaA': 1.8e-7, 'LTA': 2.0e-7, 'CMSM': 0.6e-7}

    records = []
    print(f"Executing {n_samples} 1D stiff ODE simulations...")
    for i in range(n_samples):
        T_C = float(T_samples[i])
        P_bar = float(P_samples[i])
        dt_mm = float(dt_samples[i])
        mem = str(mem_samples[i])

        layout = bundle_layout(catalyst='shell_packed', d=dt_mm * 1e-3)
        res = run_dme_simulation(
            layout,
            membrane_type=mem,
            is_membrane=True,
            T_C=T_C,
            P_ret_bar=P_bar,
            L_m=1.0,
        )

        if res['success']:
            records.append({
                'T_C': T_C,
                'P_bar': P_bar,
                'dt_mm': dt_mm,
                'perm_H2O': perm_map[mem],
                'membrane': mem,
                'a_v': layout['a_v'],
                'X_CO2': res['X_CO2'],
                'Y_DME': res['Y_DME'],
                'S_DME': res['S_DME'],
                'water_removed_pct': res['water_removed_pct'],
                'carbon_balance_error': res['carbon_balance_error'],
            })

    df = pd.DataFrame(records)
    csv_path = "results/dme_doe_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved DOE dataset ({len(df)} records) to {csv_path}")

    # Step 2: Model Training & Benchmark
    print("=== Step 2: Training ML Surrogate Benchmark ===")
    features = ['T_C', 'P_bar', 'dt_mm', 'perm_H2O']
    targets = ['X_CO2', 'Y_DME', 'S_DME', 'water_removed_pct']

    X = df[features]
    y = df[targets]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    models = {
        'RandomForest': MultiOutputRegressor(RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)),
        'ExtraTrees': MultiOutputRegressor(ExtraTreesRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)),
        'GradientBoosting': MultiOutputRegressor(GradientBoostingRegressor(n_estimators=150, max_depth=4, random_state=42)),
    }

    metrics_rows = []
    trained = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        trained[name] = (model, y_pred)

        for col_idx, target_name in enumerate(targets):
            y_t = y_test.iloc[:, col_idx].values
            y_p = y_pred[:, col_idx]

            r2 = r2_score(y_t, y_p)
            mae = mean_absolute_error(y_t, y_p)
            rmse = np.sqrt(mean_squared_error(y_t, y_p))
            mape = mean_absolute_percentage_error(y_t, y_p)

            metrics_rows.append({
                'model': name,
                'target': target_name,
                'R2': r2,
                'MAE': mae,
                'RMSE': rmse,
                'MAPE_percent': mape,
            })

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_path = "results/dme_ml_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Saved benchmark metrics to {metrics_path}")
    print(metrics_df.to_string(index=False))

    # Save best model (ExtraTrees)
    best_model = trained['ExtraTrees'][0]
    joblib.dump(best_model, "results/dme_surrogate_extratrees.joblib")
    print("Saved best model to results/dme_surrogate_extratrees.joblib")

    # Step 3: Parity Plot
    print("=== Step 3: Generating Diagnostic Parity Plot ===")
    fig, axes = plt.subplots(2, 2, figsize=(10, 9), dpi=300)
    y_pred_best = trained['ExtraTrees'][1]

    titles = ['CO2 Conversion [%]', 'DME Yield [%]', 'DME Selectivity [%]', 'Water Removed [%]']
    colors = ['#334155', '#059669', '#0284c7', '#d97706']

    for i, ax in enumerate(axes.flatten()):
        y_true_col = y_test.iloc[:, i].values
        y_pred_col = y_pred_best[:, i]

        ax.scatter(y_true_col, y_pred_col, color=colors[i], alpha=0.8, edgecolors='k', s=45, label='Held-out Test (20%)')
        mn = min(y_true_col.min(), y_pred_col.min()) * 0.98
        mx = max(y_true_col.max(), y_pred_col.max()) * 1.02
        ax.plot([mn, mx], [mn, mx], 'r--', lw=1.5, label='1:1 Parity')

        r2_val = metrics_df[(metrics_df['model'] == 'ExtraTrees') & (metrics_df['target'] == targets[i])]['R2'].values[0]
        mae_val = metrics_df[(metrics_df['model'] == 'ExtraTrees') & (metrics_df['target'] == targets[i])]['MAE'].values[0]

        ax.text(0.05, 0.90, f"R² = {r2_val:.4f}\nMAE = {mae_val:.2f}%", transform=ax.transAxes,
                fontsize=9, fontweight='bold', bbox=dict(boxstyle='round', fc='white', ec='#cbd5e1', alpha=0.9))

        ax.set_title(titles[i], fontsize=11, fontweight='bold')
        ax.set_xlabel("Physics Simulation Output [%]", fontsize=9, fontweight='bold')
        ax.set_ylabel("ExtraTrees Prediction [%]", fontsize=9, fontweight='bold')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(fontsize=8, loc='lower right')

    plt.suptitle("ExtraTrees Surrogate Model Parity Benchmark: Direct CO2-to-DME CMR", fontsize=12, fontweight='bold', y=0.99)
    plt.tight_layout()
    parity_path = "figures/dme_surrogate_parity.png"
    plt.savefig(parity_path, dpi=300)
    plt.close()
    print(f"Saved parity plot to {parity_path}")

    # Step 4: Feature Importance
    print("=== Step 4: Generating Feature Importance Plot ===")
    fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
    # Average feature importances across target estimators
    importances = np.mean([est.feature_importances_ for est in best_model.estimators_], axis=0)
    feat_names = ['Temperature (T)', 'Pressure (P)', 'Tube Diameter (d)', 'Water Permeance (Π)']
    
    y_pos = np.arange(len(feat_names))
    ax.barh(y_pos, importances * 100, color='#059669', edgecolor='#065f46')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feat_names, fontsize=9, fontweight='bold')
    ax.set_xlabel("Mean Feature Importance [%]", fontsize=10, fontweight='bold')
    ax.set_title("Global Feature Importance (ExtraTrees Surrogate on DME CMR)", fontsize=11, fontweight='bold')
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)

    for i, v in enumerate(importances * 100):
        ax.text(v + 0.8, i, f"{v:.1f}%", va='center', fontsize=9, fontweight='bold', color='#065f46')

    plt.tight_layout()
    feat_path = "figures/dme_feature_importance.png"
    plt.savefig(feat_path, dpi=300)
    plt.close()
    print(f"Saved feature importance to {feat_path}")
    print(">> All steps completed successfully.")


if __name__ == '__main__':
    main()
