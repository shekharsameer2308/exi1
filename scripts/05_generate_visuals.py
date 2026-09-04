"""
Generates complete set of publication-grade figures and ML diagnostics.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import simulate_reactor
from src.emethanol.visualization import generate_publication_figures, setup_matplotlib_style, COLORS


def generate_ml_and_research_visuals():
    print("=== Generating Research Visualizations and ML Diagnostics ===")
    out_dir = Path("results/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    setup_matplotlib_style()

    # 1. Physics figures (01 to 11)
    generate_publication_figures(str(out_dir))

    # 2. ML Parity & Residual Figures (12, 13)
    preds_path = Path("results/ml_predictions.csv")
    if preds_path.exists():
        df_preds = pd.read_csv(preds_path)
        
        # Figure 12: Surrogate Parity Plots (4 subplots)
        fig, axes = plt.subplots(2, 2, figsize=(10, 9), dpi=300)
        targets = [
            ("co2_conversion", "CO2 Conversion", axes[0, 0]),
            ("meoh_yield", "MeOH Yield", axes[0, 1]),
            ("meoh_selectivity", "MeOH Selectivity", axes[1, 0]),
            ("h2o_removal_fraction", "H2O Removal Fraction", axes[1, 1]),
        ]

        for target_key, title, ax in targets:
            if f"actual_{target_key}" in df_preds.columns:
                y_act = df_preds[f"actual_{target_key}"] * 100.0
                y_pred = df_preds[f"pred_{target_key}"] * 100.0
                ax.scatter(y_act, y_pred, color=COLORS["slate"], alpha=0.7, edgecolors="none", s=30)
                
                # 1:1 parity line
                min_v = min(y_act.min(), y_pred.min())
                max_v = max(y_act.max(), y_pred.max())
                ax.plot([min_v, max_v], [min_v, max_v], color=COLORS["emerald"], lw=2.0, ls="--", label="1:1 Parity")
                ax.set_xlabel("Physics Engine Value (%)")
                ax.set_ylabel("ML Surrogate Prediction (%)")
                ax.set_title(title)
                ax.grid(True)
                ax.legend(frameon=True)

        plt.suptitle("ML Surrogate vs Deterministic Physics Parity Benchmark", fontsize=13, y=0.98)
        plt.tight_layout()
        fig.savefig(out_dir / "12_surrogate_parity.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        print("Saved 12_surrogate_parity.png")

        # Figure 13: Residual Distribution Plots
        fig, axes = plt.subplots(2, 2, figsize=(10, 8), dpi=300)
        for i, (target_key, title, ax) in enumerate(targets):
            if f"residual_{target_key}" in df_preds.columns:
                res = df_preds[f"residual_{target_key}"] * 100.0
                sns.histplot(res, kde=True, ax=ax, color=COLORS["cyan"], edgecolor="white")
                ax.axvline(0, color=COLORS["red"], ls="--", lw=1.5)
                ax.set_xlabel("Prediction Residual (%)")
                ax.set_ylabel("Frequency")
                ax.set_title(f"Residuals: {title}")
                ax.grid(True)
        plt.suptitle("Surrogate Prediction Error Residuals", fontsize=13, y=0.98)
        plt.tight_layout()
        fig.savefig(out_dir / "13_surrogate_residuals.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        print("Saved 13_surrogate_residuals.png")

    # 3. Figure 14: Feature Importance
    model_path = Path("surrogate_rf.joblib")
    if model_path.exists():
        model = joblib.load(model_path)
        features = ["T_in_K", "P_in_bar", "flow_mol_s", "h2_co2_ratio", "water_permeance"]
        # Feature importances for each estimator
        if hasattr(model, "estimators_"):
            fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
            target_labels = ["CO2 Conv", "MeOH Yield", "MeOH Sel", "H2O Removal"]
            data_imp = {}
            for i, est in enumerate(model.estimators_[:len(target_labels)]):
                data_imp[target_labels[i]] = est.feature_importances_
            
            df_imp = pd.DataFrame(data_imp, index=features)
            df_imp.plot(kind="bar", ax=ax, colormap="viridis", width=0.8)
            ax.set_ylabel("Normalized Gini Feature Importance")
            ax.set_title("Random Forest Surrogate Feature Importance Ranking")
            ax.set_xticklabels(["T_in (K)", "P_in (bar)", "Flow (mol/s)", "H2/CO2 Ratio", "H2O Permeance"], rotation=30)
            ax.grid(True, axis="y")
            ax.legend(frameon=True)
            plt.tight_layout()
            fig.savefig(out_dir / "14_feature_importance.png", dpi=300, bbox_inches="tight")
            # Also save to outputs/ for backward compatibility
            fig.savefig("outputs/feature_importance.png", dpi=300, bbox_inches="tight")
            plt.close(fig)
            print("Saved 14_feature_importance.png")

    # 4. Figure 15: Optimization Landscape
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    temps = np.linspace(463.15, 533.15, 25)
    pressures = np.linspace(30.0, 80.0, 25)
    T_grid, P_grid = np.meshgrid(temps, pressures)
    
    # Fast proxy grid evaluation
    yield_grid = np.zeros_like(T_grid)
    for r in range(25):
        for c in range(25):
            res = simulate_reactor(temperature=float(T_grid[r, c]), pressure=float(P_grid[r, c]), total_flow=0.015, h2_co2_ratio=3.0, water_permeance=1.5e-7)
            yield_grid[r, c] = res.meoh_yield * 100.0

    cf = ax.contourf(T_grid - 273.15, P_grid, yield_grid, levels=25, cmap="magma")
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Methanol Yield (%)")
    
    # Mark global optimum
    max_idx = np.unravel_index(np.argmax(yield_grid), yield_grid.shape)
    opt_T = T_grid[max_idx] - 273.15
    opt_P = P_grid[max_idx]
    ax.scatter([opt_T], [opt_P], color="#ffffff", edgecolor="#000000", s=120, marker="*", label=f"Optimal ({opt_T:.1f} °C, {opt_P:.0f} bar)", zorder=5)

    ax.set_xlabel("Inlet Temperature (°C)")
    ax.set_ylabel("Operating Pressure (bar)")
    ax.set_title("Reactor Optimization Performance Landscape (Methanol Yield)")
    ax.grid(True, color="#ffffff", alpha=0.3)
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig(out_dir / "15_optimization_landscape.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved 15_optimization_landscape.png")
    print("\nAll 15 publication-grade figures successfully generated in results/figures/")


if __name__ == "__main__":
    generate_ml_and_research_visuals()
