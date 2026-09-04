"""
Master runner script: Executes all data generation pipelines, sweeps, ML training, optimization,
visualizations, and re-executes the Jupyter notebook to update all cell outputs and datasets.
"""
import sys
import subprocess
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


def run_pipeline():
    python_bin = sys.executable
    print(f"=== Running Full Scientific E-Methanol Pipeline using: {python_bin} ===")

    steps = [
        ("01_run_baseline.py", [python_bin, "scripts/01_run_baseline.py"]),
        ("02_run_sweeps.py", [python_bin, "scripts/02_run_sweeps.py"]),
        ("03_generate_doe.py", [python_bin, "scripts/03_generate_doe.py"]),
        ("04_train_surrogate.py", [python_bin, "scripts/04_train_surrogate.py"]),
        ("05_generate_visuals.py", [python_bin, "scripts/05_generate_visuals.py"]),
        ("06_run_optimization.py", [python_bin, "scripts/06_run_optimization.py"]),
    ]

    for name, cmd in steps:
        print(f"\n---> Executing {name}...")
        res = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error in {name}:\n{res.stderr}")
            sys.exit(1)
        else:
            print(res.stdout.strip())

    # Re-execute Jupyter notebook in-place
    nb_path = ROOT_DIR / "notebooks" / "01_Surrogate_Predictor.ipynb"
    if nb_path.exists():
        print(f"\n---> Re-executing notebook: {nb_path.name}...")
        from scripts.execute_notebook import execute_notebook
        execute_notebook(str(nb_path), working_dir=str(ROOT_DIR / "notebooks"))

    print("\n=======================================================")
    print("ALL DATA GENERATION AND NOTEBOOK EXECUTION COMPLETE!")
    print("=======================================================")


if __name__ == "__main__":
    run_pipeline()
