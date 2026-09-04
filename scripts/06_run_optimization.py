"""
Script to execute constrained reactor optimization and mandatory physics engine verification.
"""
import sys
import json
from pathlib import Path
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.optimization import optimize_reactor_physics, is_in_training_domain


def run_optimization():
    print("=== Executing Constrained Reactor Optimization & Physics Verification ===")
    
    surrogate = None
    model_path = Path("surrogate_rf.joblib")
    if model_path.exists():
        try:
            surrogate = joblib.load(model_path)
            print("Loaded serialized ML surrogate model.")
        except Exception as e:
            print(f"Could not load surrogate: {e}")

    opt_results = optimize_reactor_physics(
        objective="max_yield",
        min_selectivity=0.85,
        max_temperature_K=540.0,
        surrogate_model=surrogate,
    )

    print("\n--- Optimal Operating Conditions ---")
    for k, v in opt_results["optimal_conditions"].items():
        print(f"  {k:20s}: {v:.4f}")

    print("\n--- Verified Physics Engine Output at Optimum ---")
    phys = opt_results["physics_result"]
    print(f"  CO2 Conversion:     {phys['co2_conversion']*100:.2f}%")
    print(f"  MeOH Yield:         {phys['meoh_yield']*100:.2f}%")
    print(f"  MeOH Selectivity:   {phys['meoh_selectivity']*100:.2f}%")
    print(f"  H2O Removal:        {phys['h2o_removal_fraction']*100:.2f}%")
    print(f"  Outlet Temperature: {phys['outlet_temperature']-273.15:.2f} °C (Max: {phys['max_temperature']-273.15:.2f} °C)")

    if "co2_conversion" in opt_results["surrogate_result"]:
        surr = opt_results["surrogate_result"]
        errs = opt_results["prediction_error"]
        print("\n--- ML Surrogate vs Physics Engine Comparison ---")
        print(f"  Surrogate CO2 Conv: {surr['co2_conversion']*100:.2f}% (Error: {errs['co2_conversion_error']*100:.3f}%)")
        print(f"  Surrogate Yield:    {surr['meoh_yield']*100:.2f}% (Error: {errs['meoh_yield_error']*100:.3f}%)")

    # Safety domain check
    in_domain, domain_msg = is_in_training_domain(opt_results["optimal_conditions"])
    print(f"\nTraining Domain Status: {domain_msg}")

    # Save summary
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "optimization_summary.json", "w") as f:
        json.dump(opt_results, f, indent=4)
    print("\nOptimization results saved to results/optimization_summary.json")


if __name__ == "__main__":
    run_optimization()
