# Design of Experiments (DOE) & Automated Quality Control

**Generator**: `scripts/03_generate_doe.py`  
**Dataset**: `data/membrane_doe.csv` (500 Validated Samples)  
**Metadata**: `data/doe_metadata.json`  

---

## 1. Sampling Methodology
- **Sampling Scheme**: Latin Hypercube Sampling (LHS) for space-filling coverage across 5 operational dimensions.
- **Random Seed**: Fixed deterministic seed `42`.

### Parameter Ranges
| Feature | Range | Unit |
|---|---|---|
| Inlet Temperature ($T_{\text{in}}$) | 463.15 – 523.15 (190 – 250 °C) | $\text{K}$ |
| Operating Pressure ($P_{\text{in}}$) | 30.0 – 70.0 | $\text{bar}$ |
| Inlet Feed Flow ($F_{\text{in}}$) | 0.010 – 0.030 | $\text{mol/s}$ |
| $\text{H}_2/\text{CO}_2$ Ratio | 2.5 – 4.0 | - |
| Water Permeance ($Q_{\text{H}_2\text{O}}$) | $0.5\times 10^{-7}$ – $2.5\times 10^{-7}$ | $\text{mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$ |

---

## 2. Automated Physical Quality Control (QC) Pipeline
Before any simulation enters the training dataset, it must pass 6 verification gates:
1. **ODE Solver Convergence**: `sol.success == True` with non-stiff transition.
2. **Finite Value Check**: No `NaN`, `Inf`, or division-by-zero occurrences.
3. **Non-Negativity**: Positive molar flows $F_i(z) \ge 0$ and mole fractions $0 \le y_i(z) \le 1$.
4. **Physical Metrics Bounds**: Conversion $0 \le X \le 1$, Selectivity $0 \le S \le 1$, Yield $0 \le Y \le 1$.
5. **Elemental Balance Tolerance**: Relative error for Carbon, Hydrogen, and Oxygen $< 1.0\times 10^{-3}$.
6. **Thermal Stability**: Bed temperature within physical limits ($T \le 1000\text{ K}$).

Rejected simulations are automatically isolated in `data/invalid_cases.csv` with full diagnostic error logs.
