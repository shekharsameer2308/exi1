"""Generate a Design of Experiments (DOE) dataset from the validated model.

Each row is a simulated membrane-reactor case with randomised operating
conditions.  The DOE is used downstream to train a machine-learning
surrogate (script 04).

All data in this file is SIMULATED, not experimental.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from emethanol.reactor import ReactorConfig, simulate_reactor

rng = np.random.default_rng(7)
N_SAMPLES = 200
rows = []
failed = 0

print(f"Generating {N_SAMPLES} DOE cases (membrane reactor, non-isothermal)...")

for i in range(N_SAMPLES):
    values = dict(
        inlet_temperature_k=rng.uniform(463.15, 533.15),    # 190 - 260 C
        inlet_pressure_bar=rng.uniform(20, 70),
        inlet_flow_mol_s=rng.uniform(0.008, 0.030),
        h2_co2_ratio=rng.uniform(3.0, 4.0),
        length_m=rng.uniform(0.5, 2.0),
        water_permeance_mol_m2_s_pa=10 ** rng.uniform(-8.0, -6.3),
        sweep_water_partial_pressure_bar=10 ** rng.uniform(-5, -2),
        membrane_enabled=True,
        isothermal=False,
    )
    try:
        result = simulate_reactor(ReactorConfig(**values))
        row = {**values, **result.metrics, "data_source": "simulated_doe"}
        rows.append(row)
    except RuntimeError:
        failed += 1
        continue

    if (i + 1) % 50 == 0:
        print(f"  {i + 1}/{N_SAMPLES} completed ({failed} failed)")

out = ROOT / "outputs" / "membrane_doe.csv"
out.parent.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(out, index=False)
print(f"\nWrote {len(rows)} successful simulations to {out}")
if failed:
    print(f"  ({failed} cases failed to converge and were skipped)")
