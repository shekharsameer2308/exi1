import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to python path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import MembraneReactor1D

def generate_synthetic_data(n_samples: int = 200, output_path: str = "membrane_doe.csv"):
    """Generates a Design of Experiments (DOE) dataset by solving the physical ODEs."""
    print(f"Generating {n_samples} DOE cases using 1D Membrane Reactor Physics...")
    rng = np.random.default_rng(42)
    
    # Generate randomized inputs
    T_in = rng.uniform(463.15, 523.15, n_samples)      # 190°C to 250°C
    P_in = rng.uniform(30.0, 70.0, n_samples)          # 30 to 70 bar
    h2_co2_ratio = rng.uniform(2.5, 4.0, n_samples)    # Stoichiometric is 3.0
    flow_in = rng.uniform(0.01, 0.03, n_samples)       # Total inlet flow [mol/s]
    
    reactor = MembraneReactor1D(length=1.0, diameter=0.02)
    
    results = []
    for i in range(n_samples):
        # Solve the ODE for each condition
        res = reactor.simulate(
            T_in=T_in[i],
            P_in=P_in[i],
            flow_in=flow_in[i],
            h2_co2_ratio=h2_co2_ratio[i]
        )
        
        results.append({
            "T_in_K": T_in[i],
            "P_in_bar": P_in[i],
            "h2_co2_ratio": h2_co2_ratio[i],
            "flow_mol_s": flow_in[i],
            "co2_conversion": res["co2_conversion"],
            "meoh_yield": res["meoh_yield"]
        })
        
        if (i+1) % 50 == 0:
            print(f"[{i+1}/{n_samples}] simulations completed.")
            
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"DOE Data saved to {output_path}")

if __name__ == "__main__":
    generate_synthetic_data()
