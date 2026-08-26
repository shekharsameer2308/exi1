"""Run conventional PBR vs membrane-reactor comparison.

This script simulates both configurations at identical inlet conditions and
reports the key performance indicators (KPIs) defined in the project scope.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from emethanol.reactor import ReactorConfig, simulate_reactor

out_dir = ROOT / "outputs"
out_dir.mkdir(exist_ok=True)

# Define cases
cases = {
    "pbr": ReactorConfig(
        membrane_enabled=False,
        isothermal=False,
    ),
    "membrane_reactor": ReactorConfig(
        membrane_enabled=True,
        isothermal=False,
    ),
}

rows = []
for name, config in cases.items():
    print(f"\n{'='*50}")
    print(f"Simulating: {name}")
    print(f"{'='*50}")
    result = simulate_reactor(config)

    # Save axial profiles
    profile_df = pd.DataFrame({
        "z_m": result.z_m,
        **result.flows_mol_s,
        "temperature_k": result.temperature_k,
        "pressure_bar": result.pressure_bar,
    })
    profile_path = out_dir / f"{name}_profiles.csv"
    profile_df.to_csv(profile_path, index=False)
    print(f"  Profiles saved to {profile_path}")

    # Collect metrics
    row = {"case": name, **result.metrics}
    rows.append(row)

    # Print metrics
    for k, v in result.metrics.items():
        print(f"  {k:40s} = {v:.6f}")

# Summary table
summary = pd.DataFrame(rows)
summary_path = out_dir / "reactor_case_summary.csv"
summary.to_csv(summary_path, index=False)

print(f"\n{'='*50}")
print("Comparison Summary")
print(f"{'='*50}")
print(summary.to_string(index=False))
print(f"\nSaved to {summary_path}")
