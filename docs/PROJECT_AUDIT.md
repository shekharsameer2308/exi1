# Project Audit: E-Methanol Membrane Reactor

**Date**: 2026-09-04  
**Repository**: `https://github.com/shekharsameer2308/exi1`  
**Auditor**: Senior CRE & SciML Engineer  

---

## 1. Current Reactor Equations
The baseline 1D differential equation integrates species molar flow rates $F_i$ ($i \in \{\text{CO}_2, \text{H}_2, \text{CO}, \text{MeOH}, \text{H}_2\text{O}\}$):
$$\frac{dF_i}{dz} = \rho_{\text{cat}} A_{\text{cs}} \sum_{j} \nu_{ij} r_j - \pi D J_i$$
where:
- $\rho_{\text{cat}} = 1100.0 \text{ kg/m}^3$ (catalyst bed density)
- $A_{\text{cs}} = \frac{\pi D^2}{4}$ (reactor cross-sectional area, $D = 0.02\text{ m}$)
- $\nu_{ij}$ is the stoichiometric coefficient matrix for reactions $j \in \{\text{MeOH}, \text{RWGS}\}$
- $J_i = [0, 0, 0, 0, J_{\text{H}_2\text{O}}]^T$ is the membrane permeation flux

---

## 2. Current State Vector
$$\mathbf{F}(z) = \begin{bmatrix} F_{\text{CO}_2}(z) \\ F_{\text{H}_2}(z) \\ F_{\text{CO}}(z) \\ F_{\text{MeOH}}(z) \\ F_{\text{H}_2\text{O}}(z) \end{bmatrix} \quad [\text{mol/s}]$$

---

## 3. Current Independent Variable
- Axial position $z \in [0, L]$ with $L = 1.0\text{ m}$.

---

## 4. Species Included
1. $\text{CO}_2$ (Carbon Dioxide)
2. $\text{H}_2$ (Hydrogen)
3. $\text{CO}$ (Carbon Monoxide)
4. $\text{CH}_3\text{OH}$ / $\text{MeOH}$ (Methanol)
5. $\text{H}_2\text{O}$ (Water Vapor)

---

## 5. Reaction Network
- **Reaction 1 (CO2 Hydrogenation to Methanol)**:
  $$\text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O} \quad (\Delta H^\circ_{298} \approx -49.5\text{ kJ/mol})$$
- **Reaction 2 (Reverse Water-Gas Shift / RWGS)**:
  $$\text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O} \quad (\Delta H^\circ_{298} \approx +41.2\text{ kJ/mol})$$

---

## 6. Current Kinetic Equations
Based on Vanden Bussche & Froment (1996) LHHW formulation:
$$r_{\text{meoh}} = \frac{k_{5a} p_{\text{CO}_2} p_{\text{H}_2} \left(1 - \frac{p_{\text{MeOH}} p_{\text{H}_2\text{O}}}{K_{\text{eq},1} p_{\text{CO}_2} p_{\text{H}_2}^3}\right)}{\left(1 + K_{\text{H}_2\text{O}/K_{\text{H}_2}^{0.5}} \frac{p_{\text{H}_2\text{O}}}{\sqrt{p_{\text{H}_2}}} + K_{\text{H}_2}^{0.5} \sqrt{p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}\right)^3}$$

$$r_{\text{rwgs}} = \frac{(k_1 \cdot 10^{-4}) p_{\text{CO}_2} p_{\text{H}_2} \left(1 - \frac{p_{\text{CO}} p_{\text{H}_2\text{O}}}{K_{\text{eq},3} p_{\text{CO}_2} p_{\text{H}_2}}\right)}{1 + K_{\text{H}_2\text{O}/K_{\text{H}_2}^{0.5}} \frac{p_{\text{H}_2\text{O}}}{\sqrt{p_{\text{H}_2}}} + K_{\text{H}_2}^{0.5} \sqrt{p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}}$$

*(Note: The legacy script incorporated an uncalibrated multiplier of $10^{-4}$ on $k_1$.)*

---

## 7. Current Kinetic Constants
- $k_{5a} = 2.18 \times 10^{12} \exp\left(-\frac{87500}{RT}\right) \text{ mol}/(\text{kg}_{\text{cat}}\cdot\text{s}\cdot\text{bar}^2)$
- $k_1 = 1.22 \times 10^{10} \exp\left(-\frac{94765}{RT}\right) \text{ mol}/(\text{kg}_{\text{cat}}\cdot\text{s}\cdot\text{bar}^2)$
- $K_{\text{H}_2\text{O}/K_{\text{H}_2}^{0.5}} = 6.62 \times 10^{-11} \exp\left(\frac{124119}{RT}\right) \text{ bar}^{-0.5}$
- $K_{\text{H}_2}^{0.5} = 0.499 \exp\left(\frac{17197}{RT}\right) \text{ bar}^{-0.5}$
- $K_{\text{H}_2\text{O}} = 6.37 \times 10^{-9} \exp\left(\frac{113700}{RT}\right) \text{ bar}^{-1}$
- $\log_{10} K_{\text{eq},1} = \frac{3066}{T} - 10.592 \quad [\text{bar}^{-2}]$
- $\log_{10} K_{\text{eq},3} = -\frac{2073}{T} + 2.029 \quad [\text{dimensionless}]$

---

## 8. Current Units
- Partial pressures: $\text{bar}$
- Temperature $T$: $\text{Kelvin}$ ($R = 8.314 \text{ J/(mol}\cdot\text{K)}$)
- Reaction rates: $\text{mol}/(\text{kg}_{\text{cat}}\cdot\text{s})$
- Catalyst bed density $\rho_{\text{cat}}$: $\text{kg/m}^3$
- Permeance: $\text{mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$

---

## 9. Current Membrane Flux Equation
$$J_{\text{H}_2\text{O}} = Q_{\text{H}_2\text{O}} \cdot (p_{\text{H}_2\text{O}} \times 10^5) \quad [\text{mol}/(\text{m}^2\cdot\text{s})]$$
where $Q_{\text{H}_2\text{O}} = 1.0 \times 10^{-7} \text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$.

---

## 10. Current Membrane Assumptions
- Strictly selective for $\text{H}_2\text{O}$ (infinite selectivity over $\text{CO}_2, \text{H}_2, \text{CO}, \text{CH}_3\text{OH}$).
- Sweep side partial pressure of $\text{H}_2\text{O}$ is assumed identically zero ($p_{\text{sweep},\text{H}_2\text{O}} = 0$).
- Permeance is temperature-independent.
- Zero boundary layer mass transfer resistance.

---

## 11. Current Energy Balance
- **Isothermal assumption**: Despite docstring notes, $T(z) \equiv T_{\text{in}}$. No differential equation for temperature is integrated ($dT/dz = 0$).

---

## 12. Current Pressure Assumptions
- **Isobaric assumption**: $P(z) \equiv P_{\text{in}}$. Pressure drop along the packed bed is neglected ($dP/dz = 0$).

---

## 13. Current Boundary Conditions
At $z = 0$:
- $F_{\text{CO}_2}(0) = \frac{F_{\text{in}}}{1 + (\text{H}_2/\text{CO}_2)}$
- $F_{\text{H}_2}(0) = F_{\text{in}} - F_{\text{CO}_2}(0)$
- $F_{\text{CO}}(0) = 0.0$
- $F_{\text{MeOH}}(0) = 0.0$
- $F_{\text{H}_2\text{O}}(0) = 0.0$

---

## 14. Current Solver
- `scipy.integrate.solve_ivp` with backward differentiation formula (`method="BDF"`).

---

## 15. Solver Tolerances
- Relative tolerance: `rtol = 1e-6`
- Absolute tolerance: `atol = 1e-9`

---

## 16. DOE Ranges
- $T_{\text{in}} \in [463.15, 523.15] \text{ K}$ ($190^\circ\text{C} - 250^\circ\text{C}$)
- $P_{\text{in}} \in [30.0, 70.0] \text{ bar}$
- $\text{H}_2/\text{CO}_2 \in [2.5, 4.0]$
- $F_{\text{in}} \in [0.01, 0.03] \text{ mol/s}$
- Sampling: Uniform random distribution via `np.random.default_rng(42)`.

---

## 17. Current ML Features
1. `T_in_K`
2. `P_in_bar`
3. `h2_co2_ratio`
4. `flow_mol_s`

---

## 18. Current ML Targets
1. `co2_conversion`
2. `meoh_yield`

---

## 19. Current Train/Test Split
- 85% Train / 15% Test (`test_size=0.15`, random seed 42).

---

## 20. Current $R^2$ and Error Metrics
- Single overall multioutput $R^2$ score reported ($\sim 0.99$).
- No per-target $R^2$, MAE, RMSE, or MAPE.

---

## 21. Current Streamlit Functionality
- Single-page dashboard with 4 sliders for operational inputs.
- 2 metric summary cards for $\text{CO}_2$ Conversion and Methanol Yield.
- 1 temperature sweep 2D curve plot.

---

## 22. Current Physical Limitations
1. Isothermal behavior neglects the exothermicity of methanol synthesis.
2. Isobaric assumption neglects bed compaction and high-velocity pressure losses.
3. Zero-sweep membrane driving force neglects finite sweep dynamics and sweep-side accumulation.
4. Absence of elemental conservation verification (Carbon, Hydrogen, Oxygen).
5. Lack of axial profile inspection and spatial performance contour generation.
6. Absence of traditional reactor (TR) comparison baseline.
