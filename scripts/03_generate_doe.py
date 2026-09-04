"""
Design of Experiments (DOE) generator with Latin Hypercube Sampling and Physical Quality Control.
"""
import sys
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import MembraneReactor1D, ModelConfig, simulate_reactor


def generate_latin_hypercube_samples(n_samples: int, bounds: dict, seed: int = 42) -> pd.DataFrame:
    """Generates space-filling Latin Hypercube Samples across bounded parameter dimensions."""
    rng = np.random.default_rng(seed)
    n_dim = len(bounds)
    result = {}

    for name, (low, high) in bounds.items():
        # Stratified sampling in n_samples intervals
        intervals = np.linspace(low, high, n_samples + 1)
        samples = rng.uniform(intervals[:-1], intervals[1:])
        rng.shuffle(samples)
        result[name] = samples

    return pd.DataFrame(result)


def generate_doe_dataset(
    n_samples: int = 500,
    output_path: str = "data/membrane_doe.csv",
    invalid_path: str = "data/invalid_cases.csv",
    seed: int = 42,
    sampling_method: str = "LHS",
):
    """
    Executes DOE generation with automated physical quality control filtering.
    """
    print(f"=== Generating {n_samples} DOE cases using {sampling_method} sampling ===")
    t0 = time.time()

    bounds = {
        "T_in_K": (463.15, 523.15),
        "P_in_bar": (30.0, 70.0),
        "flow_mol_s": (0.010, 0.030),
        "h2_co2_ratio": (2.5, 4.0),
        "water_permeance": (0.5e-7, 2.5e-7),
    }

    if sampling_method == "LHS":
        df_inputs = generate_latin_hypercube_samples(n_samples, bounds, seed=seed)
    else:
        rng = np.random.default_rng(seed)
        df_inputs = pd.DataFrame({
            "T_in_K": rng.uniform(bounds["T_in_K"][0], bounds["T_in_K"][1], n_samples),
            "P_in_bar": rng.uniform(bounds["P_in_bar"][0], bounds["P_in_bar"][1], n_samples),
            "flow_mol_s": rng.uniform(bounds["flow_mol_s"][0], bounds["flow_mol_s"][1], n_samples),
            "h2_co2_ratio": rng.uniform(bounds["h2_co2_ratio"][0], bounds["h2_co2_ratio"][1], n_samples),
            "water_permeance": rng.uniform(bounds["water_permeance"][0], bounds["water_permeance"][1], n_samples),
        })

    valid_records = []
    invalid_records = []

    for i, row in df_inputs.iterrows():
        res = simulate_reactor(
            temperature=float(row["T_in_K"]),
            pressure=float(row["P_in_bar"]),
            total_flow=float(row["flow_mol_s"]),
            h2_co2_ratio=float(row["h2_co2_ratio"]),
            water_permeance=float(row["water_permeance"]),
            membrane_enabled=True,
            non_isothermal=True,
        )

        res_dict = res.to_dict()
        record = {
            "T_in_K": float(row["T_in_K"]),
            "P_in_bar": float(row["P_in_bar"]),
            "flow_mol_s": float(row["flow_mol_s"]),
            "h2_co2_ratio": float(row["h2_co2_ratio"]),
            "water_permeance": float(row["water_permeance"]),
            **res_dict
        }

        if res.is_physically_valid and res.solver_success:
            valid_records.append(record)
        else:
            invalid_records.append({
                **record,
                "rejection_reason": res.validation_message,
            })

        if (i + 1) % 100 == 0:
            print(f"[{i+1}/{n_samples}] simulations evaluated...")

    elapsed = time.time() - t0
    df_valid = pd.DataFrame(valid_records)
    df_invalid = pd.DataFrame(invalid_records)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(invalid_path).parent.mkdir(parents=True, exist_ok=True)

    df_valid.to_csv(output_path, index=False)
    # Also sync with outputs/ for backwards compatibility
    df_valid.to_csv("outputs/membrane_doe.csv", index=False)
    df_invalid.to_csv(invalid_path, index=False)

    # Save metadata
    metadata = {
        "model_version": "2.0.0",
        "kinetic_model": "VBF",
        "membrane_model": "LDF",
        "solver": "scipy.solve_ivp_BDF",
        "n_samples_requested": n_samples,
        "n_valid_accepted": len(df_valid),
        "n_invalid_rejected": len(df_invalid),
        "elapsed_seconds": elapsed,
        "random_seed": seed,
        "sampling_method": sampling_method,
    }
    with open("data/doe_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\nDOE Dataset generated in {elapsed:.2f} s:")
    print(f"  Valid samples saved to:   {output_path} ({len(df_valid)} cases)")
    print(f"  Invalid samples saved to: {invalid_path} ({len(df_invalid)} cases)")


if __name__ == "__main__":
    generate_doe_dataset(n_samples=500, sampling_method="LHS")
