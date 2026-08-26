"""Train a random-forest surrogate on the DOE dataset.

The surrogate approximates the first-principles model for rapid design
screening.  It is NOT independent experimental validation.

Outputs:
  outputs/surrogate_feature_importance.csv
  Console: test R2, MAE, feature importance ranking
"""
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
doe_path = ROOT / "outputs" / "membrane_doe.csv"

if not doe_path.exists():
    raise FileNotFoundError(
        f"DOE file not found: {doe_path}\n"
        "Run scripts/03_generate_doe.py first."
    )

df = pd.read_csv(doe_path)
print(f"Loaded {len(df)} DOE rows from {doe_path}")

# Features and targets
features = [
    "inlet_temperature_k",
    "inlet_pressure_bar",
    "inlet_flow_mol_s",
    "h2_co2_ratio",
    "length_m",
    "water_permeance_mol_m2_s_pa",
    "sweep_water_partial_pressure_bar",
]
targets = [
    "co2_conversion",
    "methanol_selectivity_carbon",
    "methanol_sty_kg_m3cat_h",
]

# Check all columns present
missing = [c for c in features + targets if c not in df.columns]
if missing:
    raise KeyError(f"Missing columns in DOE data: {missing}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df[features], df[targets], test_size=0.25, random_state=42,
)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

out_dir = ROOT / "outputs"
out_dir.mkdir(exist_ok=True)

# Train a separate model for each target and report metrics
all_importance = []

for target in targets:
    print(f"\n{'='*50}")
    print(f"Target: {target}")
    print(f"{'='*50}")

    model = RandomForestRegressor(
        n_estimators=400,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train[target])
    pred = model.predict(X_test)

    r2 = r2_score(y_test[target], pred)
    mae = mean_absolute_error(y_test[target], pred)
    print(f"  Test R2  : {r2:.4f}")
    print(f"  Test MAE : {mae:.6f}")

    perm_imp = permutation_importance(
        model, X_test, y_test[target],
        n_repeats=15, random_state=42, n_jobs=-1,
    )
    for feat, imp in sorted(
        zip(features, perm_imp.importances_mean), key=lambda x: -x[1]
    ):
        print(f"    {feat:40s} {imp:.4f}")
        all_importance.append({
            "target": target,
            "feature": feat,
            "permutation_importance": imp,
        })

# Save combined feature importance table
imp_df = pd.DataFrame(all_importance)
imp_path = out_dir / "surrogate_feature_importance.csv"
imp_df.to_csv(imp_path, index=False)
print(f"\nFeature importance saved to {imp_path}")
