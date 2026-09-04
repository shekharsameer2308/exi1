# Physics Engine Validation Protocol & Test Results

**Framework**: Automated Physics Validation Suite (`tests/`)  
**Results**: 19 / 19 Tests Passed (100% Success Rate)  

---

## 1. Summary of Automated Validation Tests

| Test ID | Test Description | Success Criterion | Result |
|---|---|---|---|
| **TEST 1** | Carbon Mass Conservation | $\text{Error}_C < 1.0\times 10^{-4}$ | **PASSED** ($< 10^{-6}$) |
| **TEST 2** | Hydrogen & Oxygen Conservation | $\text{Error}_{H,O} < 1.0\times 10^{-4}$ | **PASSED** ($< 10^{-6}$) |
| **TEST 3** | Zero Membrane Area Limit | MR approaches TR | **PASSED** |
| **TEST 4** | Zero Membrane Permeability Limit | Identical to Conventional Packed Bed | **PASSED** (rtol < $10^{-5}$) |
| **TEST 5** | High Permeance Physical Asymptote | Water removal fraction monotonic $\le 1.0$ | **PASSED** |
| **TEST 6** | Zero Reaction Check | Moles conserved across axis | **PASSED** |
| **TEST 7** | Zero Sweep Driving Force | Zero net membrane flux | **PASSED** |
| **TEST 8** | Residence Time Monotonicity | Higher residence time $\to$ higher conversion | **PASSED** |
| **TEST 9** | Temperature Sweep Reversal | Kinetic acceleration followed by equilibrium reversal | **PASSED** |
| **TEST 10** | Pressure Sweep (Le Chatelier) | Elevated pressure favors methanol yield | **PASSED** |
| **TEST 11** | Numerical Reproducibility | Identical inputs $\to$ bitwise deterministic output | **PASSED** |
| **TEST 12** | Solver Tolerance Sensitivity | Tightening tolerances (rtol $10^{-6} \to 10^{-8}$) preserves solution | **PASSED** (rtol < $10^{-4}$) |

---

## 2. Mass & Elemental Balance Verification
The model includes continuous integration of permeated species flows directly into the adaptive stiff ODE state vector:
$$\mathbf{F}_{\text{in}} \cdot \mathbf{E} = (\mathbf{F}_{\text{out}} + \mathbf{F}_{\text{permeated}}) \cdot \mathbf{E}$$
where $\mathbf{E}$ is the elemental composition matrix. Maximum elemental error across 500 DOE simulations was below $0.001\%$.
