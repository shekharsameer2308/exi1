# Baseline Model Performance & Diagnostics

**Date**: 2026-09-04  
**Script**: `scripts/01_run_baseline.py`  
**Dataset**: `results/baseline/baseline_doe.csv`  

---

## 1. Baseline Single-Run Operating Conditions

| Parameter | Symbol | Value | Unit |
|---|---|---|---|
| Inlet Temperature | $T_{\text{in}}$ | 493.15 (220.0 °C) | $\text{K}$ |
| Inlet Pressure | $P_{\text{in}}$ | 50.0 | $\text{bar}$ |
| Inlet Molar Flow | $F_{\text{in}}$ | 0.015 | $\text{mol/s}$ |
| $\text{H}_2/\text{CO}_2$ Ratio | $R_{\text{H}_2/\text{CO}_2}$ | 3.0 | - |
| Water Permeance | $Q_{\text{H}_2\text{O}}$ | $1.0 \times 10^{-7}$ | $\text{mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$ |
| Reactor Length | $L$ | 1.0 | $\text{m}$ |
| Reactor Inner Diameter | $D$ | 0.02 | $\text{m}$ |
| Catalyst Bed Density | $\rho_{\text{cat}}$ | 1100.0 | $\text{kg/m}^3$ |

---

## 2. Baseline Performance Metrics

| Metric | Baseline Value | Description |
|---|---|---|
| $\text{CO}_2$ Conversion | **3.63%** | Percent of inlet $\text{CO}_2$ consumed |
| Methanol Yield | **3.24%** | Moles of $\text{CH}_3\text{OH}$ formed per mole of inlet $\text{CO}_2$ |
| Methanol Selectivity | **89.29%** | $\text{CH}_3\text{OH} / (\text{CH}_3\text{OH} + \text{CO})$ |
| Solver Runtime | **16.08 ms** | Time for stiff BDF ODE integration |
| Solver Status | **Converged** | 0 integration failures observed |

---

## 3. Baseline DOE & Surrogate Results (500 Samples)

- **DOE Generation Time**: 3.01 s for 500 samples
- **DOE Success Rate**: 100% (500 / 500 converged)
- **Surrogate Architecture**: MultiOutputRegressor(RandomForestRegressor(n_estimators=100, max_depth=10))

### Surrogate Test Performance (15% Holdout, N=75)
| Target | $R^2$ | MAE | RMSE |
|---|---|---|---|
| $\text{CO}_2$ Conversion | 0.9755 | 0.0035 (0.35%) | 0.0065 |
| Methanol Yield | 0.9744 | 0.0032 (0.32%) | 0.0060 |
| Overall Multioutput | 0.9750 | 0.0034 | - |

---

## 4. Key Limitations Identified in Baseline

1. **Low Conversion Regime**: Due to the small reactor dimensions ($L=1\text{ m}, D=0.02\text{ m}$) at high space velocities ($F_{\text{in}} = 0.015\text{ mol/s}$ corresponds to $\sim 171\text{ L(STP)/h}$ over $0.345\text{ kg}$ catalyst), conversion remains in the initial kinetic regime ($\sim 3-4\%$).
2. **Missing Thermal Feedback**: Baseline does not compute reaction heat generation ($\Delta H_{\text{rxn}} < 0$).
3. **No Sweep Gas Mass Transfer Balance**: Assumed sweep side is pure sink.
4. **Absence of Validation Constraints**: No mass or elemental conservation tests were performed.
