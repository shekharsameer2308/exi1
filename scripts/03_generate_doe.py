import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to python path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.emethanol.reactor import MembraneReactor1D, ODENonConvergenceError

def generate_synthetic_data(n_samples: int = 200, output_path: str = "membrane_doe.csv"):
    """Generates a deterministic Design of Experiments (DOE) dataset."""
    print(f"Generating {n_samples} DOE cases using 1D Membrane Reactor Physics...")
    
    # EXPLICIT STATE: Fixed seed guarantees deterministic output
    rng = np.random.default_rng(42)
    
    T_in = rng.uniform(463.15, 523.15, n_samples)
    P_in = rng.uniform(30.0, 70.0, n_samples)
    h2_co2_ratio = rng.uniform(2.5, 4.0, n_samples)
    flow_in = rng.uniform(0.01, 0.03, n_samples)
    
    reactor = MembraneReactor1D(length=1.0, diameter=0.02)
    results = []
    failures = 0
    
    for i in range(n_samples):
        try:
            res = reactor.simulate(
                T_in=T_in[i],
                P_in=P_in[i],
                flow_in=flow_in[i],
                h2_co2_ratio=h2_co2_ratio[i]
            )
            
            results.append({
                "T_in_K": float(T_in[i]),
                "P_in_bar": float(P_in[i]),
                "h2_co2_ratio": float(h2_co2_ratio[i]),
                "flow_mol_s": float(flow_in[i]),
                "co2_conversion": res["co2_conversion"],
                "meoh_yield": res["meoh_yield"]
            })
        except ODENonConvergenceError as e:
            # HOSTILE INPUT HANDLING: Safely catch and skip unphysical boundary cases
            failures += 1
            print(f"Warning: Case {i} failed to converge -> {str(e)}")
            continue
        except Exception as e:
            # CATCH FIRE: Unexpected errors must hard fail
            raise RuntimeError(f"Unexpected critical failure at iteration {i}: {str(e)}") from e
        
        if (i+1) % 50 == 0:
            print(f"[{i+1}/{n_samples}] simulations completed.")
            
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"DOE Data saved to {output_path}. Successful cases: {n_samples - failures}/{n_samples}")

if __name__ == "__main__":
    generate_synthetic_data()
