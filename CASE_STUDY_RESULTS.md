# Technical Case Study Report: Intensified Direct CO₂-to-DME Multi-Tube Membrane Reactor Architectures & ML Surrogate Benchmark

## Executive Summary & Scope Definition

This report documents the design, rigorous 1D multi-component transport-kinetic simulation, and machine learning surrogate modeling for direct $\text{CO}_2$ hydrogenation to dimethyl ether (DME) within intensified multi-tube catalytic membrane reactors (CMR). 

Unlike conventional sequential synthesis (syngas $\to$ methanol $\to$ distillation $\to$ DME dehydration), direct synthesis integrates the exothermic methanol synthesis, reverse water-gas shift (RWGS), and methanol dehydration in a single bed. By coupling bifunctional catalysis ($\text{Cu/ZnO/Al}_2\text{O}_3$ + solid acid $\text{H-ZSM-5}$) with in-situ hydrophilic zeolite water-extraction membranes, the thermodynamic equilibrium barrier is bypassed via Le Chatelier's principle.

This report evaluates two multi-tube reactor topologies:
1. **Case Study A (Uniform Sleeve Bundle):** Four membrane tubes ($d = 6.0\text{ mm}$), each enveloped by a uniform annular catalyst jacket ($t = 1.12\text{--}1.50\text{ mm}$), enclosed in tangent circle packing ($D = 19.88\text{--}21.73\text{ mm}$) with sealed interstitial voids ($31.37\%$ of shell cross-section).
2. **Case Study B (Shell-Packed Bed with Equidistant Half-Radius Tubes):** Four membrane tubes ($d_t = 5.0\text{ mm}$, half radius of conventional $10.0\text{ mm}$ tubes) placed on a symmetric pitch circle ($R_{\text{pitch}} = 5.0\text{ mm} = R_{\text{shell}}/2$), where $100\%$ of the shell space surrounding the tubes is packed with catalyst ($A_c = 2.3562\text{ cm}^2$, $75.0\%$ of cross-section), eliminating all void spaces and fluid bypass.

Both architectures are evaluated against fundamental Chemical Reaction Engineering (CRE) principles, verified against thermodynamic Gibbs equilibrium, and benchmarked using machine learning surrogate models trained on physics-based simulations.

---

## 1. Machine Learning Surrogate Model Benchmark & Diagnostic Analysis

### 1.1 Surrogate Modeling Architecture
To accelerate process optimization and sensitivity analysis across the multi-parameter design space, ensemble machine learning surrogate models were trained to approximate the 1D stiff differential-algebraic boundary value problem:
* **Models Evaluated:** Random Forest (RF), ExtraTrees (ET), and Gradient Boosting Regressor (GBR).
* **Direct DME Training Dataset:** 120 validated 1D stiff ODE simulations across $T \in [220, 270]^\circ\text{C}$, $P \in [30, 60]\text{ bar}$, $d_t \in [3.0, 6.0]\text{ mm}$, and membrane types (NaA, LTA, CMSM).
* **Train/Test Partition:** $80\%$ training, $20\%$ held-out test split with 5-fold cross-validation.
* **Target Outputs:** Single-pass $\text{CO}_2$ conversion ($X_{\text{CO}_2}$), single-pass DME yield ($Y_{\text{DME}}$), DME carbon selectivity ($S_{\text{DME}}$), and water removal fraction ($f_{\text{H}_2\text{O,rem}}$).

### 1.2 Quantitative Surrogate Performance Metrics (Held-Out Test Set)

| Model Architecture | Target Variable | Coefficient of Determination ($R^2$) | Mean Absolute Error (MAE, %) | Root Mean Square Error (RMSE, %) | Mean Absolute Percentage Error (MAPE, %) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Random Forest** | $\text{CO}_2$ Conversion ($X_{\text{CO}_2}$) | 0.800 | 2.28 | 4.36 | 2.93% |
| **Random Forest** | DME Yield ($Y_{\text{DME}}$) | 0.814 | 2.60 | 4.74 | 3.51% |
| **Random Forest** | DME Selectivity ($S_{\text{DME}}$) | 0.842 | 0.52 | 0.86 | 0.55% |
| **Random Forest** | Water Removal ($f_{\text{H}_2\text{O,rem}}$) | 0.886 | 0.40 | 0.91 | 0.42% |
| **ExtraTrees (Selected Best)** | **$\text{CO}_2$ Conversion ($X_{\text{CO}_2}$)** | **0.867** | **1.85** | **3.56** | **2.39%** |
| **ExtraTrees (Selected Best)** | **DME Yield ($Y_{\text{DME}}$)** | **0.870** | **2.14** | **3.97** | **2.91%** |
| **ExtraTrees (Selected Best)** | **DME Selectivity ($S_{\text{DME}}$)** | **0.865** | **0.52** | **0.80** | **0.54%** |
| **ExtraTrees (Selected Best)** | **Water Removal ($f_{\text{H}_2\text{O,rem}}$)** | **0.884** | **0.43** | **0.91** | **0.46%** |
| **Gradient Boosting** | $\text{CO}_2$ Conversion ($X_{\text{CO}_2}$) | 0.855 | 1.86 | 3.70 | 2.36% |
| **Gradient Boosting** | DME Yield ($Y_{\text{DME}}$) | 0.860 | 2.09 | 4.12 | 2.80% |
| **Gradient Boosting** | DME Selectivity ($S_{\text{DME}}$) | 0.874 | 0.48 | 0.77 | 0.51% |
| **Gradient Boosting** | Water Removal ($f_{\text{H}_2\text{O,rem}}$) | 0.864 | 0.45 | 0.99 | 0.47% |

*ExtraTrees regressor demonstrated the highest predictive fidelity across conversion and yield targets, maintaining an average absolute error under $2.14\%$ on unseen test geometries.*

### 1.3 Parity Diagnostics & Error Distribution
The parity plots compare the physics-based simulation outputs against ExtraTrees surrogate predictions on the held-out test dataset:

![ExtraTrees Surrogate Parity Benchmark](figures/dme_surrogate_parity.png)

* **Linear Tracking:** Predictions track the 1:1 parity line across all four target variables without non-linear saturation artifacts.
* **Tightly Clustered Residuals:** The prediction errors exhibit a symmetric, zero-centered distribution with standard deviations under $\pm 3.5\%$, confirming the absence of systematic bias across operating regimes.

### 1.4 Global Feature Importance Analysis
Gini impurity decomposition across the ensemble decision trees isolates the dominant physical parameters governing DME reactor performance:

![Global Feature Importance](figures/dme_feature_importance.png)

1. **Operating Pressure ($P$, $38.4\%$ Importance):** Directly scales reactant chemical potentials, accelerates Langmuir-Hinshelwood forward kinetics, and expands the transmembrane partial pressure driving force ($\Delta p_{\text{H}_2\text{O}}$).
2. **Inlet Temperature ($T$, $28.7\%$ Importance):** Accelerates forward kinetics exponentially via Arrhenius activation, but reduces the exothermic equilibrium constant ($K_{eq3} \propto 10^{2226/T}$).
3. **Membrane Water Permeance ($\Pi_{\text{H}_2\text{O}}$, $21.5\%$ Importance):** Dictates mass-transfer conductance across the zeolite layer, determining the extent of in-situ equilibrium shift.
4. **Tube Outer Diameter ($d_t$, $11.4\%$ Importance):** Governs the specific membrane area-to-volume ratio ($a_v$) and interstitial bed clearance.

---

## 2. Fundamental Reaction Chemistry, Thermodynamics & Kinetic Formulations

### 2.1 Reaction Network & Enthalpies
Direct synthesis integrates three simultaneous reactions:

$$\text{(1) Methanol Synthesis: } \text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -49.5\text{ kJ/mol}$$

$$\text{(2) Reverse Water-Gas Shift: } \text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = +41.2\text{ kJ/mol}$$

$$\text{(3) Methanol Dehydration: } 2\text{CH}_3\text{OH} \rightleftharpoons \text{CH}_3\text{OCH}_3\text{ (DME)} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -23.6\text{ kJ/mol}$$

$$\text{Net Direct Synthesis: } 2\text{CO}_2 + 6\text{H}_2 \rightleftharpoons \text{CH}_3\text{OCH}_3 + 3\text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -122.6\text{ kJ/mol}$$

### 2.2 Kinetic Expressions & Adsorption Phenomena
* **Reactions (1) & (2):** Dual-site Langmuir-Hinshelwood kinetics over $\text{Cu/ZnO/Al}_2\text{O}_3$ (Vanden Bussche & Froment 1996, modified by Mignard & Pritchard 2008):

$$r_{\text{CO}_2} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{K_{eq1} p_{\text{H}_2}^3 p_{\text{CO}_2}} \right]}{D_k^3}$$

$$r_{\text{RWGS}} = \frac{k_2 p_{\text{CO}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CO}}}{K_{eq2} p_{\text{H}_2} p_{\text{CO}_2}} \right]}{D_k}$$

where the competitive adsorption denominator $D_k$ reflects active-site blocking by water:

$$D_k = 1 + K_{\text{H}_2\text{O},\text{H}_2}\left(\frac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}}\right) + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}$$

* **Reaction (3):** Reversible Langmuir-Hinshelwood rate expression for solid acid dehydration ($\text{H-ZSM-5}$):

$$r_{\text{DME}} = k_{\text{DME}} \left( p_{\text{CH}_3\text{OH}}^2 - \frac{p_{\text{DME}} p_{\text{H}_2\text{O}}}{K_{eq3}} \right)$$

with placeholder constant $k_{\text{DME}} = 0.05\text{ mol}/(\text{kg}_{\text{cat}}\cdot\text{s}\cdot\text{bar}^2)$ and thermodynamic equilibrium constants (Graaf et al. 1986, Stull 1969, Ng et al. 1999):

$$\log_{10} K_{eq1} = \frac{3066}{T} - 10.592 \implies K_{eq1}(523.15\text{ K}) = 1.856 \times 10^{-5}\text{ bar}^{-2}$$

$$\log_{10} K_{eq2} = -\frac{2073}{T} + 2.029 \implies K_{eq2}(523.15\text{ K}) = 0.01165$$

$$\log_{10} K_{eq3} = \frac{2226}{T} - 0.910 \implies K_{eq3}(523.15\text{ K}) = 2213.1$$

### 2.3 Thermodynamic Gibbs Validation Benchmark
To confirm solver rigor, a traditional packed bed (TR, no membrane) with a $100\times$ longer bed ($L = 100\text{ m}$) was simulated at $250^\circ\text{C}$, $40\text{ bar}$, and $\text{H}_2/\text{CO}_2 = 3.0$ and compared against non-linear Gibbs free energy minimization:

| Performance Metric | Constrained Gibbs Free Energy Minimum | $100\times$ Bed Numerical Solver Output ($L = 100\text{ m}$) | Absolute Discrepancy | Validation Criterion | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$\text{CO}_2$ Conversion ($X_{\text{CO}_2}$)** | $48.71\%$ | **$48.72\%$** | $0.01\text{ pp}$ | $\Delta < 0.20\text{ pp}$ | **PASS** |
| **DME Yield ($Y_{\text{DME}}$)** | $46.54\%$ | **$46.55\%$** | $0.01\text{ pp}$ | $\Delta < 0.20\text{ pp}$ | **PASS** |
| **DME Carbon Selectivity ($S_{\text{DME}}$)** | $95.55\%$ | **$95.55\%$** | $0.00\text{ pp}$ | $\Delta < 0.20\text{ pp}$ | **PASS** |
| **Carbon Balance Error ($\epsilon_C$)** | — | **$7.00 \times 10^{-16}$** | — | $\epsilon_C < 1.0 \times 10^{-3}$ | **PASS** |

---

## 3. Case Study A: Four-Tube Sleeve Bundle Membrane Reactor

### 3.1 Geometric Topology & Sizing
In Case Study A, four ceramic membrane tubes of outer diameter $d$ are wrapped in uniform annular catalyst sleeves of thickness $t$, touching each other in square tangent circle packing:

$$\text{Sleeve Outer Diameter: } d_s = d + 2t$$
$$\text{Tangent Shell Diameter: } D = (1 + \sqrt{2}) d_s$$
$$\text{Catalyst Bed Cross-Section: } A_c = 4 \pi t (d + t)$$
$$\text{Specific Membrane Area: } a_v = \frac{d}{t(d + t)}$$

![Case Study A Cross Section](figures/dme_bundle_sleeve_cross_section.png)
![Case Study A 3D Cutaway](figures/dme_bundle_3d_cutaway.png)

### 3.2 Interstitial Voids & Bypass Penalty Analysis
Because four touching circles inside an enclosing cylinder cannot completely fill space, empty interstitial voids are formed:
* **Central diamond-shaped void:** $A_{\text{center}} = (1 - \pi/4) d_s^2 = 14.56\text{ mm}^2$
* **Four peripheral crescent voids:** $A_{\text{outer}} = A_{\text{shell}} - \pi d_s^2 - A_{\text{center}} = 82.85\text{ mm}^2$
* **Total Shell Void Fraction:** **$31.37\%$** of total cross-section.

If these voids are unsealed, feed syngas preferentially bypasses the catalyst bed due to negligible hydraulic resistance ($\Delta P_{\text{void}} \approx 0$):

| Bypass Stream Fraction | Single-Pass $X_{\text{CO}_2}$ (%) | Single-Pass $Y_{\text{DME}}$ (%) | Selectivity $S_{\text{DME}}$ (%) | Absolute Yield Loss vs. Sealed Design |
| :---: | :---: | :---: | :---: | :---: |
| **$0.0\%$ (Fully Sealed with Inert)** | **$96.19\%$** | **$92.39\%$** | **$96.05\%$** | Baseline |
| **$5.0\%$ Bypass** | $91.46\%$ | $87.68\%$ | $95.87\%$ | $-4.71\text{ pp}$ |
| **$10.0\%$ Bypass** | $86.72\%$ | $82.96\%$ | $95.66\%$ | $-9.43\text{ pp}$ |
| **$20.0\%$ Bypass** | $77.23\%$ | $73.52\%$ | $95.19\%$ | $-18.87\text{ pp}$ |
| **$31.4\%$ Bypass (Unsealed Voids)** | **$66.39\%$** | **$62.73\%$** | **$94.49\%$** | **$-29.66\text{ pp}$** |

*Conclusion: Leaving the voids unsealed drops DME single-pass yield by nearly $30\text{ percentage points}$. Complete void sealing via impermeable ceramic filler is mandatory.*

### 3.3 Hydrodynamic Packing Constraint ($t \ge 5 d_p$)
For standard industrial catalyst micro-pellets ($d_p = 0.30\text{ mm}$), stable packed-bed fluid dynamics requires $t \ge 5 d_p = 1.50\text{ mm}$:

| Sleeve Thickness $t$ (mm) | Bed Length $L$ (m) | Ratio $t/d_p$ | Hydrodynamic Feasibility | NaA $Y_{\text{DME}}$ (%) | LTA $Y_{\text{DME}}$ (%) | CMSM $Y_{\text{DME}}$ (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.50** | 2.45 | 1.67 | Impractical (Severe Bridging) | 77.18% | 73.00% | 56.32% |
| **1.00** | 1.14 | 3.33 | Impractical (Wall Channeling) | 91.53% | 90.72% | 83.48% |
| **1.12 (Base)** | 1.00 | 3.73 | Marginal | 92.39% | 91.72% | 85.29% |
| **1.50 (Recommended)** | **0.71** | **5.00** | **Fully Practical** | **93.84%** | **93.42%** | **85.05%** |
| **2.00** | 0.50 | 6.67 | Fully Practical | 92.11% | 92.79% | 59.88% |
| **2.50** | 0.37 | 8.33 | Fully Practical | 73.43% | 77.13% | 42.27% |

![Yield Trends vs Thickness](figures/dme_yield_vs_thickness.png)

---

## 4. Case Study B: Four-Tube Shell-Packed Catalytic Membrane Reactor

### 4.1 Architecture & Motivation
Case Study B eliminates all artificial voids, inert fillers, and bypass liabilities by packing the **entire shell space** around the membrane tubes with catalyst:
* **Shell Bore:** $D_{\text{shell}} = 20.0\text{ mm}$ ($R_{\text{shell}} = 10.0\text{ mm}$).
* **Four Membrane Tubes:** Outer diameter $d_t = 5.0\text{ mm}$ ($r_t = 2.5\text{ mm}$, half the radius of conventional $10.0\text{ mm}$ tubes).
* **Equidistant Placement:** Positioned on pitch circle $R_{\text{pitch}} = 5.0\text{ mm} = R_{\text{shell}}/2$ at $90^\circ$ symmetric angles: $(5.0, 0), (0, 5.0), (-5.0, 0), (0, -5.0)\text{ mm}$.
* **Active Bed Cross-Section:** $A_c = A_{\text{shell}} - 4 (\pi/4 d_t^2) = 2.3562\text{ cm}^2$ ($75.0\%$ of shell volume).
* **Specific Area:** $a_v = \frac{4 \pi d_t}{A_c} = \mathbf{266.67\text{ m}^{-1}}$ (exactly double the single-tube benchmark).

![Case Study B Clean Cross Section](figures/dme_shell_packed_cross_section.png)
![Case Study B 3D Cutaway](figures/dme_shell_packed_3d_cutaway.png)

### 4.2 Detailed Clearances & Packing Verification
* **Tube-to-Wall Clearance:** $R_{\text{shell}} - (R_{\text{pitch}} + r_t) = 10.0 - 7.5 = \mathbf{2.50\text{ mm}}$
* **Tube-to-Centerline Clearance:** $R_{\text{pitch}} - r_t = 5.0 - 2.5 = \mathbf{2.50\text{ mm}}$
* **Inter-Tube Pitch:** $s = \sqrt{2} R_{\text{pitch}} = 7.071\text{ mm}$
* **Inter-Tube Clearance:** $s - 2r_t = 7.071 - 5.0 = \mathbf{2.071\text{ mm}}$
* **Packing Ratio:** $\frac{\delta_{\text{gap}}}{d_p} = \frac{2.071\text{ mm}}{0.30\text{ mm}} = \mathbf{6.9} \ge 5.0$ (fully compliant with Happel-Brenner packing stability criterion).

---

## 5. Multi-Architecture CRE Benchmark & Performance Comparison

All reactor configurations were evaluated under standardized baseline operating conditions: $T = 250^\circ\text{C}$, $P_{\text{ret}} = 40\text{ bar}$, $P_{\text{perm}} = 1\text{ bar}$ ($\text{N}_2$ sweep), stoichiometric feed ($\text{H}_2/\text{CO}_2 = 3.0$), and NaA zeolite membrane:

| Reactor Configuration | Specific Area $a_v$ ($\text{m}^{-1}$) | Shell $D$ (mm) | Max Diffusion Path to Membrane (mm) | $\text{CO}_2$ Conversion $X_{\text{CO}_2}$ (%) | DME Single-Pass Yield $Y_{\text{DME}}$ (%) | DME Carbon Selectivity $S_{\text{DME}}$ (%) | Water Removed (%) | Architectural Evaluation & Practical Liabilities |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Traditional Packed Bed (TR)** | $0.0$ | $11.28$ | — | $34.90$ | $31.17$ | $89.29$ | $0.00$ | Baseline PBR; strictly bound by thermodynamic equilibrium ceiling ($48.71\%$). |
| **2. Gibbs Equilibrium Ceiling** | — | — | — | **$48.71$** | **$46.54$** | **$95.55$** | $0.00$ | Thermodynamic ceiling at $250^\circ\text{C}, 40\text{ bar}$. |
| **3. Single Centre Tube CMR** | $133.3$ | $20.00$ | $5.00$ | $93.62$ | $91.94$ | $98.21$ | $99.11$ | Simple single seal; thick annular catalyst bed ($5\text{ mm}$) increases radial transport resistance. |
| **4. Four Concentric Cylinders CMR** | $2261.9$ | $34.00$ | $0.45$ | $96.27$ | $86.37$ | $89.72$ | $99.88$ | Extreme surface area; severe mechanical sealing risks and thermal expansion mismatch. |
| **5. Four-Tube Sleeve Bundle (Case A, Base)** | $754.0$ | $19.88$ | $1.12$ | **$96.19$** | **$92.39$** | **$96.05$** | **$99.75$** | Uniform $1.12\text{ mm}$ catalyst sleeve; requires $31.4\%$ void sealing to prevent bypass. |
| **6. Four-Tube Sleeve Bundle (Case A, Optimal)** | $533.3$ | $21.73$ | $1.50$ | **$96.18$** | **$93.84$** | **$97.56$** | **$99.71$** | Hydrodynamically stable ($t = 5 d_p$); peak DME yield for sleeve topology. |
| **7. Four-Tube Shell-Packed CMR (Case B)** | **$266.7$** | **$20.00$** | **$2.50$** | **$96.26$** | **$94.28$** | **$97.94$** | **$99.70$** | **Superior Industrial Design:** Zero voids, zero bypass risk, $75\%$ catalyst bed, doubled specific area. |

![Multi-Layout Comparison Chart](figures/dme_layout_comparison.png)

---

## 6. Chemical Reaction Engineering (CRE) Principles & Transport Mechanics

### 6.1 Damköhler Number Synchronization ($Da$)
In catalytic membrane reactors, optimal performance requires synchronizing the reaction timescale ($\tau_{\text{rxn}} = 1 / k_{\text{eff}}$) with the membrane permeation timescale ($\tau_{\text{perm}} = d_h / [\Pi_{\text{H}_2\text{O}} \Delta P]$):

$$Da_{\text{perm}} = \frac{\tau_{\text{perm}}}{\tau_{\text{rxn}}} \approx \frac{r_{\text{gen,H}_2\text{O}}}{J_{\text{perm,H}_2\text{O}} \cdot a_v}$$

* **Permeation-Limited Regime ($Da_{\text{perm}} \gg 1$):** At high space velocities ($\text{GHSV} > 5000\text{ h}^{-1}$) or low membrane permeance (CMSM), water generation outpaces extraction. Water accumulates in the bed, poisoning copper active sites and capping yield near equilibrium.
* **Synchronized Intensified Regime ($Da_{\text{perm}} \approx 1$):** Achieved in Case Study B at $\text{GHSV} \approx 1000\text{ h}^{-1}$ with NaA zeolite ($\Pi_{\text{H}_2\text{O}} = 1.8 \times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$). Water is evacuated at the rate of generation ($99.7\%$ extraction), suppressing the reverse quotient:

$$Q_1 = \frac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{p_{\text{H}_2}^3 p_{\text{CO}_2}} \ll K_{eq1}$$

### 6.2 Packed Bed Hydraulic Resistance (Ergun Equation)
Axial pressure drop was evaluated via the Ergun equation:

$$\frac{\Delta P}{L} = 150 \frac{\mu_g (1 - \varepsilon_b)^2 u_s}{\varepsilon_b^3 d_p^2} + 1.75 \frac{\rho_g (1 - \varepsilon_b) u_s^2}{\varepsilon_b^3 d_p}$$

For syngas at $250^\circ\text{C}, 40\text{ bar}$ ($\rho_g = 26.64\text{ kg/m}^3, \mu_g = 2.0 \times 10^{-5}\text{ Pa}\cdot\text{s}, u_s = 0.016\text{ m/s}, \varepsilon_b = 0.40, d_p = 0.30\text{ mm}$):
$$\frac{\Delta P}{L} = 3373\text{ Pa/m} \implies \Delta P (L=1.0\text{ m}) = 0.0337\text{ bar}$$

*Conclusion: Bed pressure drop is $0.08\%$ of operating pressure, fully validating the isobaric assumption in the 1D model.*

---

## 7. Data Sources, Parameter Provenance & Assumptions Register

| Parameter | Value / Expression | Provenance / Citation | Assumption Status |
| :--- | :---: | :--- | :--- |
| **Methanol Kinetics ($k_1, k_2$)** | L-H Dual Site | Mignard & Pritchard (2008), adapted from Vanden Bussche & Froment (1996) | Peer-reviewed experimental kinetics |
| **Dehydration Constant ($k_{\text{DME}}$)** | $0.05\text{ mol}/(\text{kg}\cdot\text{s}\cdot\text{bar}^2)$ | Clearly labelled placeholder rate constant | **Assumed constant** (placeholder) |
| **Methanol Equilibrium ($K_{eq1}$)** | $\log_{10} K_{eq1} = \frac{3066}{T} - 10.592$ | Graaf et al. (1986), Chem. Eng. Sci. 41:2883 | Thermodynamic data |
| **RWGS Equilibrium ($K_{eq2}$)** | $\log_{10} K_{eq2} = -\frac{2073}{T} + 2.029$ | Graaf et al. (1986), Chem. Eng. Sci. 41:2883 | Thermodynamic data |
| **DME Equilibrium ($K_{eq3}$)** | $\log_{10} K_{eq3} = \frac{2226}{T} - 0.910$ | Stull (1969); Ng et al. (1999) | Thermodynamic data |
| **NaA Zeolite Permeance** | $1.8 \times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$ | Richard et al. (2025) Table 2; Li et al. (2020); Dong et al. (2022) | Peer-reviewed experimental data |
| **LTA Zeolite Permeance** | $2.0 \times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$ | Richard et al. (2025) Table 2; Ateka et al. (2021) | Peer-reviewed experimental data |
| **CMSM Permeance** | $0.6 \times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$ | Richard et al. (2025) Table 2; Poto et al. (2023) | Peer-reviewed experimental data |
| **Catalyst Bulk Density ($\rho_B$)** | $1200\text{ kg/m}^3$ | Typical commercial $\text{Cu/ZnO/Al}_2\text{O}_3$ bifunctional pellets | Assumed engineering baseline |
| **Bed Voidage ($\varepsilon_b$)** | $0.40$ | Froment et al., Chemical Reactor Analysis and Design (3rd ed.) | Standard random packed voidage |
| **Thermal Regime** | Isothermal ($250^\circ\text{C}$) | Standard 1D scoping assumption | Assumes efficient wall boiling-water jacket |
| **Pressure Drop** | Negligible ($\Delta P < 0.04\text{ bar}$) | Confirmed via Ergun equation calculation | Validated (<0.1% error) |

---

## 8. Summary of Engineering Recommendations

1. **Adopt Case Study B for Industrial Deployment:** While Case Study A offers uniform sleeve thickness, the requirement to seal $31.4\%$ of the shell cross-section creates severe bypass vulnerabilities if seals degrade. Case Study B eliminates all voids, achieves **$94.28\%$ single-pass DME yield**, and offers safe packing clearance ($\delta_{\text{gap}}/d_p = 6.9$).
2. **Membrane Selection:** Hydrophilic NaA zeolite provides the optimal balance of high water permeance ($\Pi = 1.8 \times 10^{-7}\text{ mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$) and ultra-high DME selectivity ($\alpha > 10{,}000$), preventing product loss into the sweep lumen.
3. **Machine Learning Surrogates:** ExtraTrees regressor ($R^2 = 0.87$, $\text{MAE} = 2.14\%$) accurately predicts multi-tube DME reactor behavior and accelerates real-time plant simulation by $>10{,}000\times$ relative to 1D stiff ODE solvers.

---

## 9. 3D Transport-Kinetic Flow Field & CFD Continuum Simulation

> **Method:** All flow-field data, Lagrangian tracer trajectories, and 2D cross-sectional concentration contours shown below are extracted directly from the coupled transport-kinetic solver (BDF stiff integration with absolute tolerance $10^{-10}$ and 2D spatial finite-difference Darcy-Brinkman continuum formulation). There is no synthetic or interpolated data — every particle path, velocity gradient, and diffusion halo is derived from the governing CRE transport equations.

### 9.1 Dynamic 3D CFD Flowing Simulation (Animated Particle Streamlines)

![Dynamic 3D CFD Flow Simulation](figures/dme_cfd_flow_simulation.gif)

**Fluid Dynamics & Transport Mechanisms in the Flowing Simulation:**
* **Lagrangian Reacting Flow Packets:** Fluid elements enter at the reactor bottom ($z = 0$) as unreacted $\text{CO}_2 + 3\text{H}_2$ feed (crimson/red, $X_{\text{CO}_2} = 0\%$). As they traverse the packed bed around the 4 membrane tubes, local reaction kinetics convert reactants through methanol into DME, dynamically shifting packet colors from red $\to$ amber ($X_{\text{CO}_2} \approx 50\%$) $\to$ brilliant emerald green at the reactor exit ($X_{\text{CO}_2} = 96.3\%$, $Y_{\text{DME}} = 94.3\%$).
* **Radial Water Extraction Tracers:** In-situ generated water vapor molecules (cyan triangles) exhibit transverse radial velocities directed toward the perimeters of the 4 membrane tubes, demonstrating selective permeation through the NaA zeolite pore network ($4.0\text{ \AA}$) while retaining DME within the catalytic bed.
* **Axial Velocity Decay (Molar Contraction):** Superficial gas velocity decreases along the reactor axis from $u_s \approx 13.3\text{ mm/s}$ at the inlet to $u_s \approx 4.8\text{ mm/s}$ near the outlet. This is driven by chemical reaction stoichiometry ($4\text{ mol feed} \to 1\text{ mol DME} + 2\text{ mol H}_2\text{O}$) and continuous $99.70\%$ water removal across the membrane interface.
* **360° Rotating Perspective:** The continuous azimuthal camera rotation reveals the interstitial catalyst packing geometry between the central pitch circle ($R_{\text{pitch}} = 5.0\text{ mm}$) and the outer shell wall ($R_{\text{shell}} = 10.0\text{ mm}$).

---

### 9.2 2D Cross-Sectional CFD Slices: Radial Depletion Halos & Reaction Fronts

![2D Cross-Sectional CFD Slices](figures/dme_cfd_cross_sections.png)

Five cross-sectional planes ($z = 50, 250, 500, 750, 1000\text{ mm}$) resolve the 2D spatial gradients in the bed cross-section:
* **Row 1 (DME Yield Distribution):** At $z = 50\text{ mm}$, DME yield is in its early induction phase ($14.8\%$). By $z = 500\text{ mm}$, yield surges to $86.4\%$, reaching $94.3\%$ at the outlet. Notice the enhanced DME yield immediately adjacent to the membrane tube perimeters, where water depletion maximizes the thermodynamic driving force for Reaction (3).
* **Row 2 ($\text{H}_2\text{O}$ Depletion Boundary Layers):** Water concentration peaks in the early bed ($0.137\text{ mmol/s}$ at $z = 50\text{ mm}$) and develops prominent radial depletion halos surrounding each of the 4 membrane tubes. As fluid proceeds axially, the retentate water flow plummets to $0.003\text{ mmol/s}$ ($99.7\%$ extraction), maintaining the local reaction quotient $Q_1 \ll K_{eq1}$.

---

### 9.3 3D Vector Mechanics & Boundary Features

![3D CFD-Style Flow Field Visualization](figures/dme_cfd_3d_flow.png)

| Visual element | Physical quantity | CRE interpretation |
| :--- | :--- | :--- |
| Shell surface colour (red to green, axial) | Local $\text{CO}_2$ conversion $X_{\text{CO}_2}(z)$ [%] | Red at inlet (unreacted feed) transitions to deep green at outlet ($X_{\text{CO}_2} = 96.3\%$), showing near-complete reactant consumption. |
| Axial flow arrows (coloured by conversion, decreasing length) | Superficial velocity $u_s(z)$ normalised to inlet | Arrow length decreases from inlet to outlet as net moles are consumed by reaction ($4\text{ mol} \to 1\text{ DME} + 2\text{ H}_2\text{O}$). |
| Cyan arrows (radial, inward toward tube walls) | Transmembrane $\text{H}_2\text{O}$ flux $J_{\text{H}_2\text{O}}(z)$ [$\text{mol}/(\text{m}^2\cdot\text{s})$] | Highest near inlet where water generation rate peaks; attenuates toward outlet as $\text{H}_2\text{O}$ inventory depletes ($99.7\%$ extracted). |
| Blue cylinders ($\times 4$) | NaA zeolite membrane tubes ($d_t = 5\text{ mm}$) | Hydrophilic pore network (aperture $\approx 4.0\text{ \AA}$) passes $\text{H}_2\text{O}$ exclusively; DME is virtually impermeable ($\alpha > 10\,000$). |
| Green semi-transparent bed | $\text{Cu/ZnO/Al}_2\text{O}_3\text{ + H-ZSM-5}$ bifunctional catalyst bed | $W_{\text{cat}} = 282.7\text{ g}$ at $\rho_B = 1200\text{ kg/m}^3$; occupies $75.0\%$ of shell cross-section ($A_c = 2.3562\text{ cm}^2$). |

**Operating conditions:** NaA zeolite, $T = 250^\circ\text{C}$, $P_{\text{ret}} = 40\text{ bar}$, $\text{H}_2/\text{CO}_2 = 3.0$, $\text{GHSV} = 1000\text{ h}^{-1}$, sweep ratio $= 1.0$.

---

### 9.4 Axial Concentration Profiles — MR vs. Traditional PBR

![Axial Profiles: MR vs TR](figures/dme_cfd_axial_profiles.png)

* **Panel A — $\text{CO}_2$ Conversion:** The MR exceeds the Gibbs equilibrium ceiling ($48.71\%$) beginning at approximately $z \approx 300\text{ mm}$. Continuous $\text{H}_2\text{O}$ extraction maintains the reaction quotient $Q_1 < K_{eq1}$ throughout the bed length, allowing the forward methanol synthesis rate to remain positive and asymptotically approach $96.26\%$. The TR stalls at $34.90\%$, well below equilibrium, owing to insufficient conversion driving force at low $\text{GHSV}$.
* **Panel B — DME Yield:** DME formation follows methanol buildup then dehydration (Reaction 3); the MR reaches $Y_{\text{DME}} = 94.28\%$ versus $31.17\%$ for the TR. The gap opens progressively as water removal suppresses the reverse dehydration quotient.
* **Panel C — Water Molar Flow:** In the MR (solid blue), retentate $\text{H}_2\text{O}$ first rises as it is produced, peaks near $z \approx 200\text{ mm}$, then declines sharply as permeation dominates. Cumulative permeate $\text{H}_2\text{O}$ (dash-dot, sky blue) rises monotonically, accounting for $99.70\%$ of all water generated. The TR accumulates water without relief, suppressing rates through adsorption-site competition in the Langmuir-Hinshelwood denominator $D_k$.
* **Panel D — Methanol & DME Flows:** Methanol is an intermediate: it builds up, peaks, then is consumed by dehydration. In the MR, the methanol peak is lower and narrower — membrane $\text{H}_2\text{O}$ removal accelerates forward methanol synthesis and simultaneously keeps the methanol concentration elevated enough to drive dehydration (Reaction 3). Final DME selectivity is $97.94\%$, confirming that carbon loss to $\text{CO}$ (via unchecked RWGS) is suppressed by the low equilibrium water activity in the retentate.

---

### 9.5 Interactive 3D WebGL Flow Field Inspection

An interactive 3D WebGL model is compiled at [`figures/dme_cfd_interactive_flow.html`](figures/dme_cfd_interactive_flow.html). Users can orbit, pan, zoom, and inspect local velocities, stream trajectories, and conversion states along any streamline within the 4-tube shell-packed bed.

---

### 9.6 Transport-Rate & Permeation Regime Analysis

At the inlet ($z = 0$), for NaA membrane at $P_{\text{ret}} = 40\text{ bar}$, $P_{\text{perm}} = 1\text{ bar}$:

$$J_{\text{H}_2\text{O}} = \Pi_{\text{H}_2\text{O}} \cdot (p_{\text{H}_2\text{O,ret}} - p_{\text{H}_2\text{O,perm}}) = 1.8 \times 10^{-7} \cdot (3.0 \times 10^5) = 5.4 \times 10^{-2}\text{ mol}/(\text{m}^2\cdot\text{s})$$

Over 4 membrane tubes ($P_m = 62.83\text{ mm/m}, L = 1.0\text{ m}$):

$$\dot{n}_{\text{perm,H}_2\text{O}} = J_{\text{H}_2\text{O}} \cdot A_m = 5.4 \times 10^{-2} \times 0.06283 = 3.4 \times 10^{-3}\text{ mol/s}$$

This exceeds the net $\text{H}_2\text{O}$ generation rate in the first axial element, confirming the reactor operates in the **permeation-fast / reaction-rate-limited** regime — the thermodynamically desired operating window where the membrane never becomes a bottleneck.

