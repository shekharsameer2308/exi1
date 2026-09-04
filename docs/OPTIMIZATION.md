# Reactor Optimization & Verified Physics Engine Pipeline

**Module**: `src/emethanol/optimization.py`  
**Script**: `scripts/06_run_optimization.py`  
**Output**: `results/optimization_summary.json`  

---

## 1. Optimization Problem Formulation

$$\max_{\mathbf{x}} \quad Y_{\text{MeOH}}(\mathbf{x})$$
$$\text{subject to:} \quad S_{\text{MeOH}}(\mathbf{x}) \ge 0.85, \quad T_{\max}(\mathbf{x}) \le 540\text{ K}, \quad \mathbf{x}_{\min} \le \mathbf{x} \le \mathbf{x}_{\max}$$

### Decision Variables ($\mathbf{x}$):
1. Inlet Temperature $T_{\text{in}} \in [463.15, 533.15]\text{ K}$
2. Operating Pressure $P_{\text{in}} \in [30.0, 80.0]\text{ bar}$
3. Inlet Flow Rate $F_{\text{in}} \in [0.008, 0.030]\text{ mol/s}$
4. $\text{H}_2/\text{CO}_2$ Ratio $\in [2.5, 4.5]$
5. Membrane Permeance $Q_{\text{H}_2\text{O}} \in [0.5\times 10^{-7}, 3.0\times 10^{-7}]\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$

---

## 2. Mandatory Scientific Rule: Direct Physics Engine Verification
In accordance with scientific reaction engineering standards:
1. Fast ML surrogate screening can be utilized to locate candidate optima.
2. **Every optimum MUST be re-simulated using the deterministic 1D non-isothermal physics engine.**
3. Final engineering performance metrics must reflect verified physical equations, not surrogate approximations alone.

---

## 3. Optimal Operating Point Results

| Parameter / Metric | Value |
|---|---|
| Optimal Temperature ($T_{\text{in}}$) | **514.2 K (241.0 °C)** |
| Optimal Pressure ($P_{\text{in}}$) | **62.6 bar** |
| Optimal Feed Flow Rate | **0.0080 mol/s** |
| Optimal $\text{H}_2/\text{CO}_2$ Ratio | **4.50** |
| Optimal Water Permeance | **$1.8\times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$** |
| **Verified $\text{CO}_2$ Conversion** | **77.49%** |
| **Verified Methanol Yield** | **71.42%** |
| **Verified Methanol Selectivity** | **92.17%** |
| **Verified $\text{H}_2\text{O}$ Removal Fraction** | **98.14%** |
| Carbon Balance Error | $< 1.0\times 10^{-6}$ |
