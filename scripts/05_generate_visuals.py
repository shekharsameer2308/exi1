import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def generate_visuals():
    print("Generating ML and Analytical visuals...")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 1. Load Data
    try:
        df = pd.read_csv("outputs/membrane_doe.csv")
        model = joblib.load("surrogate_rf.joblib")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 2. Correlation Heatmap
    plt.figure(figsize=(8, 6))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("DOE Data Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("outputs/correlation_heatmap.png", dpi=300)
    plt.close()
    print("Saved correlation_heatmap.png")

    # 3. Thermal/Pressure Heatmap (Model Inference)
    temps = np.linspace(463.15, 523.15, 50)
    pressures = np.linspace(30.0, 70.0, 50)
    T_grid, P_grid = np.meshgrid(temps, pressures)
    
    # Flatten grids for prediction
    T_flat = T_grid.flatten()
    P_flat = P_grid.flatten()
    
    # Fix other parameters to mean values
    ratio_mean = df['h2_co2_ratio'].mean()
    flow_mean = df['flow_mol_s'].mean()
    
    X_sweep = pd.DataFrame({
        'T_in_K': T_flat,
        'P_in_bar': P_flat,
        'h2_co2_ratio': ratio_mean,
        'flow_mol_s': flow_mean
    })
    
    # Predict
    preds = model.predict(X_sweep)
    meoh_yield = preds[:, 1].reshape(50, 50) * 100 # percentage
    
    plt.figure(figsize=(8, 6))
    contour = plt.contourf(T_grid, P_grid, meoh_yield, levels=20, cmap="viridis")
    plt.colorbar(contour, label="Methanol Yield (%)")
    plt.title(f"Methanol Yield Heatmap\n(Flow = {flow_mean:.3f} mol/s, H2:CO2 = {ratio_mean:.1f})")
    plt.xlabel("Temperature (K)")
    plt.ylabel("Pressure (bar)")
    plt.tight_layout()
    plt.savefig("outputs/thermal_pressure_heatmap.png", dpi=300)
    plt.close()
    print("Saved thermal_pressure_heatmap.png")

    # 4. Feature Importance
    # MultiOutputRegressor contains an 'estimators_' list for each target
    features = ['T_in_K', 'P_in_bar', 'h2_co2_ratio', 'flow_mol_s']
    targets = ['co2_conversion', 'meoh_yield']
    
    importance_df = pd.DataFrame(index=features)
    for i, target in enumerate(targets):
        rf_estimator = model.estimators_[i]
        importance_df[target] = rf_estimator.feature_importances_
        
    importance_df.to_csv("outputs/feature_importance.csv")
    
    # Plot feature importance
    importance_df.plot(kind="bar", figsize=(8, 6), colormap="Set2")
    plt.title("Random Forest Feature Importance")
    plt.ylabel("Importance Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/feature_importance.png", dpi=300)
    plt.close()
    print("Saved feature_importance.png / .csv")

if __name__ == "__main__":
    generate_visuals()
