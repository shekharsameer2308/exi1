import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_preds = pd.read_csv("results/ml_predictions.csv")
targets = [
    ("co2_conversion", "CO2 Conversion"),
    ("meoh_yield", "MeOH Yield"),
    ("meoh_selectivity", "MeOH Selectivity"),
    ("h2o_removal_fraction", "H2O Removal Fraction"),
]
fig, axes = plt.subplots(2, 2, figsize=(10, 8), dpi=300)
axes = axes.flatten()
for i, (target_key, title) in enumerate(targets):
    ax = axes[i]
    col = f"residual_{target_key}"
    print(f"Checking {col} in columns: {col in df_preds.columns}")
    if col in df_preds.columns:
        res = df_preds[col] * 100.0
        print(f"Data for {col}: len {len(res)}, NaN {res.isna().sum()}")
        sns.histplot(res, kde=True, ax=ax, color="cyan", edgecolor="white")
        ax.axvline(0, color="red", ls="--", lw=1.5)
        ax.set_title(f"Residuals: {title}")

fig.savefig("test_residuals.png")
print("Done")
