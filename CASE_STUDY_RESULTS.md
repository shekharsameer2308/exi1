# Comprehensive Case Study Results: Direct CO₂-to-DME Four-Tube Sleeve Bundle Membrane Reactor

## Executive Overview and Scope Separation

This document delivers the dedicated simulation analysis, individual reactor profiles, and comparative multi-architecture benchmarks for the intensified **Four-Tube Sleeve Bundle Catalytic Membrane Reactor (CMR)** designed for direct $\text{CO}_2$ hydrogenation to dimethyl ether (DME).

> **Scope Clarification:** This case study is completely distinct from the primary tube-in-tube reactor designs modeled elsewhere in the repository:
> - **Module A (E-Methanol Synthesis):** Annular packed bed ($\text{Cu/ZnO/Al}_2\text{O}_3$), central NaA zeolite tube ($d_m = 10\text{ mm}$), single-stage methanol synthesis from syngas.
> - **Module B (Ammonia Decomposition):** Central lumen packed bed ($\text{Ru/YSZ}$), metallic Pd membrane tube ($d_m = 10\text{ mm}$), selective $\text{H}_2$ extraction into shell.
> - **Case Study (Direct DME Synthesis, This Document):** Four-tube bundle inside a cylindrical shell where each membrane tube ($d = 6.0\text{ mm}$) is enveloped in a uniform annular catalyst sleeve ($t = 1.12\text{--}1.50\text{ mm}$) with sealed interstitial voids ($31.37\%$ of shell area), performing combined methanol synthesis and dehydration over a bifunctional catalyst.

---

## 1. Direct CO₂-to-DME Reaction Network & Kinetics

### 1.1 Reaction Stoichiometry & Thermodynamics
Direct DME synthesis integrates exothermic methanol synthesis with exothermic methanol dehydration and the endothermic reverse water-gas shift (RWGS):

$$\text{(1) } \text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -49.5\text{ kJ/mol}$$

$$\text{(2) } \text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O}\text{ (RWGS)}, \quad \Delta H^\circ_{298} = +41.2\text{ kJ/mol}$$

$$\text{(3) } 2\text{CH}_3\text{OH} \rightleftharpoons \text{CH}_3\text{OCH}_3\text{ (DME)} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -23.6\text{ kJ/mol}$$

$$\text{Net Direct Synthesis: } 2\text{CO}_2 + 6\text{H}_2 \rightleftharpoons \text{CH}_3\text{OCH}_3 + 3\text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -122.6\text{ kJ/mol}$$

### 1.2 Kinetic Formulations and Rate Laws
* **Reactions (1) & (2):** Dual-site Langmuir-Hinshelwood kinetics over commercial $\text{Cu/ZnO/Al}_2\text{O}_3$ catalyst (Vanden Bussche & Froment 1996, modified by Mignard & Pritchard 2008, validated in Hauth et al. 2025):
  $$r_{\text{CO}_2} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{K_{eq1} p_{\text{H}_2}^3 p_{\text{CO}_2}} \right]}{D_k^3}$$
  $$r_{\text{RWGS}} = \frac{k_2 p_{\text{CO}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CO}}}{K_{eq2} p_{\text{H}_2} p_{\text{CO}_2}} \right]}{D_k}$$
  where the adsorption denominator is:
  $$D_k = 1 + K_{\text{H}_2\text{O},\text{H}_2}\left(\frac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}}\right) + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}$$

* **Reaction (3):** Clearly labelled placeholder reversible Langmuir-Hinshelwood rate law representing solid acid dehydration ($\gamma\text{-Al}_2\text{O}_3$ / H-ZSM-5):
  $$r_{\text{DME}} = k_{\text{DME}} \left( p_{\text{CH}_3\text{OH}}^2 - \frac{p_{\text{DME}} p_{\text{H}_2\text{O}}}{K_{eq3}} \right)$$
  with placeholder constant $k_{\text{DME}} = 0.05\text{ mol}/(\text{kg}_{\text{cat}}\cdot\text{s}\cdot\text{bar}^2)$ and equilibrium constant $\log_{10} K_{eq3} = \frac{2226}{T} - 0.910$ (Stull 1969; Ng et al. 1999).

* **Thermodynamic Constants @ 250 °C ($523.15\text{ K}$):**
  $$K_{eq1} = 1.856 \times 10^{-5}\text{ bar}^{-2}, \quad K_{eq2} = 0.0117, \quad K_{eq3} = 2213.1$$

---

## 2. Individual Reactor Results: Four-Tube Sleeve Bundle CMR

### 2.1 Reactor Physical Dimensions & Sizing
The four-tube sleeve bundle houses four membrane tubes of outer diameter $d$, each clad in an individual catalyst sleeve of thickness $t$. The sleeves touch in a square tangent packing within an enclosing circular shell:

$$\text{Shell Diameter: } D = (1 + \sqrt{2}) d_s = (1 + \sqrt{2})(d + 2t)$$
$$\text{Catalyst Cross-Section: } A_c = 4 \pi t (d + t)$$
$$\text{Specific Membrane Area: } a_v = \frac{d}{t(d + t)}$$

| Geometric Parameter | Baseline Design ($t = 1.12\text{ mm}$) | Recommended Design ($t = 1.50\text{ mm}$)* |
| :--- | :---: | :---: |
| Membrane Tube Outer Diameter ($d$) | $6.00\text{ mm}$ ($0.006\text{ m}$) | $6.00\text{ mm}$ ($0.006\text{ m}$) |
| Catalyst Sleeve Thickness ($t$) | $1.118\text{ mm}$ ($1.12\text{ mm}$) | $1.500\text{ mm}$ ($1.50\text{ mm}$) |
| Sleeve Outer Diameter ($d_s$) | $8.236\text{ mm}$ | $9.000\text{ mm}$ |
| Shell Inner Diameter ($D$) | $19.88\text{ mm}$ | $21.73\text{ mm}$ |
| Active Bed Cross-Section ($A_c$) | $1.000\text{ cm}^2$ ($1.0 \times 10^{-4}\text{ m}^2$) | $1.414\text{ cm}^2$ ($1.414 \times 10^{-4}\text{ m}^2$) |
| Active Bed Length ($L$) | $1.000\text{ m}$ | $0.707\text{ m}$ |
| Catalyst Mass Inventory ($W_{\text{cat}}$) | $0.120\text{ kg}$ ($\rho_B = 1200\text{ kg/m}^3$) | $0.120\text{ kg}$ ($\rho_B = 1200\text{ kg/m}^3$) |
| Specific Membrane Area ($a_v$) | $754.0\text{ m}^{-1}$ | $533.3\text{ m}^{-1}$ |
| Total Membrane Area ($A_{\text{mem}}$) | $0.0754\text{ m}^2$ ($754.0\text{ cm}^2$) | $0.0533\text{ m}^2$ ($533.3\text{ cm}^2$) |
| Total Shell Cross-Section ($A_{\text{shell}}$) | $310.51\text{ mm}^2$ | $370.83\text{ mm}^2$ |
| Total Sealed Void Area ($A_{\text{void}}$) | $97.41\text{ mm}^2$ ($31.37\%$) | $116.30\text{ mm}^2$ ($31.37\%$) |
| Central Void Pocket Area ($A_{\text{center}}$) | $14.56\text{ mm}^2$ | $17.38\text{ mm}^2$ |
| Four Peripheral Voids Area ($A_{\text{outer}}$) | $82.85\text{ mm}^2$ | $98.92\text{ mm}^2$ |
| Particle Sizing Criterion ($t/d_p$, $d_p = 0.3\text{ mm}$) | $3.73$ (Impractical, bridging risk) | **$5.00$ (Hydrodynamically Stable)** |

*\*The recommended design adjusts $L$ to $0.707\text{ m}$ to maintain exact constant catalyst mass ($0.120\text{ kg}$) and constant syngas residence time while satisfying the $t \ge 5 d_p$ packing stability rule.*

---

### 2.2 Baseline Axial Profiles ($d = 6.0\text{ mm}, t = 1.12\text{ mm}, L = 1.0\text{ m}$)
Simulation conditions: $T = 250^\circ\text{C}$, $P_{\text{ret}} = 40\text{ bar}$, $P_{\text{perm}} = 1\text{ bar}$ ($\text{N}_2$ sweep ratio $S/F = 1.0$), $\text{H}_2/\text{CO}_2 = 3.0$, $\text{GHSV} = 1000\text{ h}^{-1}$, NaA zeolite membrane.

| Axial Position $z$ (m) | $F_{\text{CO}_2}$ ($\mu\text{mol/s}$) | $F_{\text{H}_2}$ ($\mu\text{mol/s}$) | $F_{\text{H}_2\text{O}}$ ($\mu\text{mol/s}$) | $F_{\text{MeOH}}$ ($\mu\text{mol/s}$) | $F_{\text{CO}}$ ($\mu\text{mol/s}$) | $F_{\text{DME}}$ ($\mu\text{mol/s}$) | $X_{\text{CO}_2}$ (%) | $Y_{\text{DME}}$ (%) | Permeate $F_{\text{H}_2\text{O}}$ ($\mu\text{mol/s}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.00** | 309.83 | 929.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **0.10** | 138.25 | 473.11 | 25.80 | 5.82 | 31.02 | 67.24 | 55.38 | 43.40 | 213.74 |
| **0.20** | 63.80 | 214.28 | 11.75 | 2.87 | 13.91 | 114.72 | 79.41 | 74.05 | 350.56 |
| **0.30** | 20.85 | 66.30 | 2.98 | 0.90 | 5.32 | 140.75 | 93.27 | 90.86 | 426.97 |
| **0.40** | 13.12 | 39.61 | 1.46 | 0.38 | 4.14 | 144.97 | 95.77 | 93.58 | 440.35 |
| **0.50** | 12.16 | 35.19 | 1.30 | 0.30 | 3.80 | 145.24 | 96.08 | 93.75 | 441.98 |
| **0.60** | 12.01 | 33.95 | 1.27 | 0.29 | 3.74 | 144.82 | 96.12 | 93.48 | 442.17 |
| **0.70** | 11.97 | 33.15 | 1.22 | 0.28 | 3.79 | 144.42 | 96.14 | 93.22 | 442.17 |
| **0.80** | 11.91 | 32.39 | 1.17 | 0.27 | 3.83 | 143.98 | 96.16 | 92.94 | 442.17 |
| **0.90** | 11.85 | 31.70 | 1.13 | 0.27 | 3.87 | 143.53 | 96.18 | 92.65 | 442.17 |
| **1.00** | **11.80** | **31.10** | **1.09** | **0.26** | **3.91** | **143.12** | **96.19** | **92.39** | **442.17** |

**Key Axial Phenomenological Milestones:**
1. **$z = 0.00\text{--}0.20\text{ m}$ (Kinetic Ignition Zone):** Rapid forward consumption of fresh syngas; DME formation accelerates as methanol intermediate dehydrates. By $z = 0.20\text{ m}$, $79.4\%$ conversion is achieved.
2. **$z = 0.20\text{--}0.40\text{ m}$ (Intense Equilibrium Bypass Zone):** Membrane flux extracts $427.0\ \mu\text{mol/s}$ of water vapor into the lumen, pulling the reversible dehydration and methanol reactions far past standard equilibrium limits. Conversion passes $95\%$.
3. **$z = 0.40\text{--}1.00\text{ m}$ (Exhaustion & Deep Water Stripping Plateau):** Free water in the catalyst bed drops to a trace level ($1.09\ \mu\text{mol/s}$), reaching **$99.75\%$** cumulative water extraction. DME yield stabilizes at **$92.39\%$** with **$96.05\%$** carbon selectivity.

---

### 2.3 Recommended Design Axial Profiles ($d = 6.0\text{ mm}, t = 1.50\text{ mm}, L = 0.707\text{ m}$)
Sizing with $t = 1.50\text{ mm}$ ($L = 0.707\text{ m}$, $W_{\text{cat}} = 0.120\text{ kg}$, $t/d_p = 5.00$):

| Axial Position $z$ (m) | $F_{\text{CO}_2}$ ($\mu\text{mol/s}$) | $F_{\text{H}_2}$ ($\mu\text{mol/s}$) | $F_{\text{H}_2\text{O}}$ ($\mu\text{mol/s}$) | $F_{\text{MeOH}}$ ($\mu\text{mol/s}$) | $F_{\text{CO}}$ ($\mu\text{mol/s}$) | $F_{\text{DME}}$ ($\mu\text{mol/s}$) | $X_{\text{CO}_2}$ (%) | $Y_{\text{DME}}$ (%) | Permeate $F_{\text{H}_2\text{O}}$ ($\mu\text{mol/s}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.00** | 438.01 | 1314.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **0.07** | 282.59 | 953.18 | 59.73 | 9.88 | 53.58 | 45.88 | 35.48 | 20.95 | 141.43 |
| **0.14** | 200.95 | 679.11 | 41.78 | 7.53 | 40.06 | 94.52 | 54.12 | 43.16 | 289.54 |
| **0.21** | 129.31 | 432.72 | 27.02 | 5.07 | 25.26 | 138.83 | 70.48 | 63.39 | 420.16 |
| **0.28** | 71.40 | 234.61 | 14.53 | 3.01 | 13.89 | 174.32 | 83.70 | 79.60 | 526.03 |
| **0.35** | 35.77 | 114.47 | 6.12 | 1.53 | 7.90 | 195.64 | 91.83 | 89.33 | 591.46 |
| **0.42** | 22.40 | 70.36 | 2.93 | 0.80 | 6.30 | 203.20 | 94.89 | 92.78 | 615.76 |
| **0.49** | 18.50 | 56.88 | 2.15 | 0.56 | 5.71 | 205.26 | 95.78 | 93.73 | 622.71 |
| **0.56** | 17.26 | 51.99 | 1.93 | 0.46 | 5.42 | 205.76 | 96.06 | 93.95 | 624.90 |
| **0.64** | 16.84 | 49.99 | 1.86 | 0.43 | 5.29 | 205.74 | 96.16 | 93.94 | 625.62 |
| **0.71** | **16.71** | **48.98** | **1.82** | **0.41** | **5.24** | **205.51** | **96.18** | **93.84** | **625.79** |

---

### 2.4 Membrane Material Performance Matrix (Richard et al. 2025 Table 2)

| Membrane Designation | Permeance $\Pi_{\text{H}_2\text{O}}$ ($\text{mol}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$) | Selectivity $\alpha(\text{H}_2\text{O}/i)$ | $\text{CO}_2$ Conversion $X_{\text{CO}_2}$ (%) | DME Yield $Y_{\text{DME}}$ (%) | DME Selectivity $S_{\text{DME}}$ (%) | Water Removed (%) | Carbon Balance Error |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NaA Zeolite (Li 2020)** | $1.8 \times 10^{-7}$ | $\text{CO}_2$: 5000, $\text{H}_2$: 1000, DME: 10000 | **96.19%** | **92.39%** | **96.05%** | **99.75%** | $5.25 \times 10^{-16}$ |
| **LTA Zeolite (Ateka 2021)** | $2.0 \times 10^{-7}$ | $\text{CO}_2$: 3000, $\text{H}_2$: 800, DME: 10000 | **96.20%** | **91.72%** | **95.34%** | **99.78%** | $1.75 \times 10^{-16}$ |
| **CMSM (Poto 2023)** | $0.6 \times 10^{-7}$ | $\text{CO}_2$: 250, $\text{H}_2$: 80, DME: 2000 | **93.89%** | **85.29%** | **90.85%** | **99.80%** | $5.25 \times 10^{-16}$ |
| **Traditional Bed (No Mem)** | — | — | **34.90%** | **31.17%** | **89.31%** | **0.00%** | $5.60 \times 10^{-16}$ |

---

### 2.5 Parametric Sensitivity: Tube Diameter ($d$) and Sleeve Thickness ($t$)

#### Table A: Diameter Sweep ($d \in [4, 10]\text{ mm}$) at Fixed $A_c = 1.0 \times 10^{-4}\text{ m}^2$ ($L = 1.0\text{ m}$)

| $d$ (mm) | $t$ (mm) | $d_s$ (mm) | $D$ (mm) | $a_v$ ($\text{m}^{-1}$) | Practicality ($t/d_p$) | NaA $Y_{\text{DME}}$ (%) | LTA $Y_{\text{DME}}$ (%) | CMSM $Y_{\text{DME}}$ (%) | Water Removed (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4.0** | 1.46 | 6.92 | 16.70 | 502.7 | Impractical ($4.86$) | 93.38 | 92.89 | 87.45 | 99.73 |
| **6.0** | 1.12 | 8.24 | 19.88 | 754.0 | Impractical ($3.73$) | 92.39 | 91.72 | 85.29 | 99.75 |
| **8.0** | 0.89 | 9.79 | 23.63 | 1005.3 | Impractical ($2.98$) | 91.39 | 90.55 | 83.03 | 99.78 |
| **10.0** | 0.74 | 11.48 | 27.72 | 1256.6 | Impractical ($2.47$) | 90.39 | 89.38 | 80.83 | 99.80 |

#### Table B: Sleeve Thickness Sweep ($t \in [0.5, 3.0]\text{ mm}$) at Constant $W_{\text{cat}} = 0.12\text{ kg}$ ($d = 6.0\text{ mm}$)

| $t$ (mm) | Bed Length $L$ (m) | $a_v$ ($\text{m}^{-1}$) | Packing Stability ($t \ge 5 d_p$) | NaA $Y_{\text{DME}}$ (%) | LTA $Y_{\text{DME}}$ (%) | CMSM $Y_{\text{DME}}$ (%) | Water Removed (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.50** | 2.45 | 1846.2 | Impractical ($1.67$) | 77.18 | 73.00 | 56.32 | 99.97 |
| **1.00** | 1.14 | 857.1 | Impractical ($3.33$) | 91.53 | 90.72 | 83.48 | 99.78 |
| **1.12** | 1.00 | 754.0 | Impractical ($3.73$) | 92.39 | 91.72 | 85.29 | 99.75 |
| **1.50** | 0.71 | 533.3 | **Practical ($5.00$)** | **93.84** | **93.42** | **85.05** | **99.71** |
| **2.00** | 0.50 | 375.0 | **Practical ($6.67$)** | 92.11 | 92.79 | 59.88 | 99.36 |
| **2.50** | 0.37 | 282.4 | **Practical ($8.33$)** | 73.43 | 77.13 | 42.27 | 95.19 |
| **3.00** | 0.29 | 222.2 | **Practical ($10.00$)** | 55.44 | 60.36 | 32.61 | 88.08 |

---

### 2.6 Void Bypass Sensitivity Analysis
The interstitial voids (central diamond pocket + four peripheral pockets) represent $31.37\%$ of the total shell cross-section. Because open voids lack Darcy bed resistance ($\Delta P \approx 0$), feed syngas preferentially channels through open voids unless sealed:

| Bypass Fraction | Effective $X_{\text{CO}_2}$ (%) | Single-Pass $Y_{\text{DME}}$ (%) | Selectivity $S_{\text{DME}}$ (%) | Yield Loss vs. Sealed Design |
| :---: | :---: | :---: | :---: | :---: |
| **$0.0\%$ (Sealed Voids)** | **$96.19\%$** | **$92.39\%$** | **$96.05\%$** | Baseline |
| **$5.0\%$ Bypass** | $91.46\%$ | $87.68\%$ | $95.87\%$ | $-4.71\text{ pp}$ |
| **$10.0\%$ Bypass** | $86.72\%$ | $82.96\%$ | $95.66\%$ | $-9.43\text{ pp}$ |
| **$20.0\%$ Bypass** | $77.23\%$ | $73.52\%$ | $95.19\%$ | $-18.87\text{ pp}$ |
| **$31.4\%$ (Area-Weighted)** | **$66.39\%$** | **$62.73\%$** | **$94.49\%$** | **$-29.66\text{ pp}$** |

---

## 3. Comparative Benchmarks: Multi-Architecture Comparison

All configurations evaluated on an identical catalyst mass basis ($W_{\text{cat}} = 0.120\text{ kg}$, $A_c = 1.0 \times 10^{-4}\text{ m}^2$, $T = 250^\circ\text{C}$, $P = 40\text{ bar}$, $\text{GHSV} = 1000\text{ h}^{-1}$, NaA zeolite membrane):

| Reactor Configuration | Specific Area $a_v$ ($\text{m}^{-1}$) | Shell Diameter $D$ (mm) | Max Diffusion Path to Wall (mm) | $\text{CO}_2$ Conversion $X_{\text{CO}_2}$ (%) | DME Yield $Y_{\text{DME}}$ (%) | DME Selectivity $S_{\text{DME}}$ (%) | Water Removed (%) | Architectural Advantages & Engineering Liabilities |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Traditional Packed Bed (TR)** | $0.0$ | $11.28$ | — | $34.90$ | $31.17$ | $89.31$ | $0.00$ | **Baseline:** Bound by Gibbs thermodynamic conversion ceiling ($48.71\%$). |
| **2. Gibbs Equilibrium (100x Bed)** | — | — | — | **$48.72$** | **$46.55$** | **$95.55$** | — | **Thermodynamic Limit:** Validated by 100x bed length ($L = 100\text{ m}$). |
| **3. One Centre Tube CMR** | $314.2$ | $15.08$ | $2.54$ | $96.27$ | $94.13$ | $97.78$ | $99.71$ | **Single-Tube Simplicity:** Simple single seal, but thick radial bed ($2.54\text{ mm}$) increases radial mass transfer resistance. |
| **4. Four Concentric Cylinders CMR** | $2261.9$ | $34.00$ | $0.45$ | $96.27$ | $86.37$ | $89.72$ | $99.88$ | **Extreme Surface Area:** High water removal, but severe mechanical complexity; concentric thermal expansion mismatches and manifold sealing risks. |
| **5. Four-Tube Shell-Packed CMR** | $754.0$ | $16.47$ | $4.20$ | $96.19$ | $92.39$ | $96.05$ | $99.75$ | **Open Shell Packing:** Catalyst fills entire shell; outer corner catalyst pellets are $>4\text{ mm}$ away from any tube, creating dead zones. |
| **6. Four-Tube Lumen-Packed CMR** | $709.0$ | $16.35$ | $2.82$ | $96.20$ | $92.57$ | $96.23$ | $99.75$ | **Lumen Catalyst:** Catalyst packed inside four $5.6\text{ mm}$ tubes; difficult catalyst dumping, repacking, and tube loading in industrial scale. |
| **7. Four-Tube Sleeve Bundle CMR (Proposed)** | **$754.0$** | **$19.88$** | **$1.12$** | **$96.19$** | **$92.39$** | **$96.05$** | **$99.75$** | **Uniform Diffusion Jacket:** $100\%$ of catalyst pellets are within exact distance $t = 1.12\text{ mm}$ of membrane; voids sealed to eliminate bypass. |
| **8. Recommended Sleeve Bundle ($t = 1.50\text{ mm}$)** | **$533.3$** | **$21.73$** | **$1.50$** | **$96.18$** | **$93.84$** | **$97.56$** | **$99.71$** | **Hydrodynamically Stable:** Satisfies $t \ge 5 d_p$ packing stability ($d_p = 0.30\text{ mm}$); peak single-pass DME yield. |

---

## 4. Case Study B: Four-Tube Shell-Packed Catalytic Membrane Reactor
*(Whole Shell Packed with Catalyst | 4 Equidistant Membrane Tubes at Half Radius)*

### 4.1 Design Philosophy & Motivation
While the uniform sleeve architecture (Case Study A) ensures an identical radial diffusion distance around each tube, it requires sealing or filling $31.37\%$ of the shell volume with inert baffles to prevent severe bypassing. 

In **Case Study B**, the reactor design is updated to eliminate all artificial voids and bypass risks:
- The **entire shell-side volume** surrounding the four membrane tubes is packed with catalyst ($A_c = 2.3562\text{ cm}^2$, representing $75.0\%$ of the shell cross-section).
- The four membrane tubes have outer diameter $d_t = 5.0\text{ mm}$ ($r_t = 2.5\text{ mm}$), which is **comparatively half the radius** of the standard $10.0\text{ mm}$ membrane tube ($r = 5.0\text{ mm}$).
- The tubes are positioned **equidistant from the center** on a pitch circle radius $R_{\text{pitch}} = 5.0\text{ mm}$ (exactly half the shell radius $R_{\text{shell}}/2 = 5.0\text{ mm}$), arranged symmetrically at $90^\circ$ angles.

![Shell-Packed Cross Section](figures/dme_shell_packed_cross_section.png)

### 4.2 Geometric Formulation & Sizing Comparison

$$\text{Shell ID: } D_{\text{shell}} = 20.0\text{ mm} \implies R_{\text{shell}} = 10.0\text{ mm}$$
$$\text{Tube OD: } d_t = 5.0\text{ mm} \implies r_t = 2.5\text{ mm} \quad (\text{comparatively half radius})$$
$$\text{Pitch Radius: } R_{\text{pitch}} = 5.0\text{ mm} = \frac{R_{\text{shell}}}{2}$$
$$\text{Tube Center Coordinates: } (\pm 5.0, 0)\text{ mm}, \quad (0, \pm 5.0)\text{ mm}$$
$$\text{Adjacent Center-to-Center Pitch: } s = \sqrt{2} R_{\text{pitch}} = 7.071\text{ mm}$$

**Cross-Sectional Area Breakdown:**
- Total Shell Interior Area: $A_{\text{shell}} = \frac{\pi}{4}(20.0)^2 = 3.1416\text{ cm}^2$
- 4 Membrane Tubes Area: $A_{\text{tubes}} = 4 \times \frac{\pi}{4}(5.0)^2 = 0.7854\text{ cm}^2$ ($25.0\%$ of shell)
- Catalyst Bed Cross-Section: $A_c = A_{\text{shell}} - A_{\text{tubes}} = 2.3562\text{ cm}^2$ ($75.0\%$ of shell)
- Membrane Perimeter: $P_m = 4 \times \pi (5.0\text{ mm}) = 62.83\text{ mm}$
- Specific Membrane Area: $a_v = \frac{P_m}{A_c} = \mathbf{266.67\text{ m}^{-1}}$ (exactly double the single 10 mm tube value of $133.33\text{ m}^{-1}$)

**Clearance & Hydrodynamic Margin:**
- Wall clearance (tube to outer shell wall): $R_{\text{shell}} - (R_{\text{pitch}} + r_t) = 10.0 - 7.5 = \mathbf{2.50\text{ mm}}$
- Centerline clearance (tube to reactor axis): $R_{\text{pitch}} - r_t = 5.0 - 2.5 = \mathbf{2.50\text{ mm}}$
- Inter-tube clearance (between adjacent tubes): $s - 2r_t = 7.071 - 5.0 = \mathbf{2.071\text{ mm}}$
- Hydrodynamic packing ratio: $\frac{\delta_{\text{gap}}}{d_p} = \frac{2.071\text{ mm}}{0.30\text{ mm}} = \mathbf{6.9} \ge 5.0$ (fully compliant with Happel-Brenner packing stability criterion, eliminating bridging and wall channeling).

### 4.3 Rigorous Simulation Performance (T = 250 °C, P = 40 bar, L = 1.0 m)

| Performance Metric | Traditional PBR (No Membrane) | Single Centre Tube ($d_m=10\text{ mm}$) | Case Study A (Sleeve Bundle, $t=1.12\text{ mm}$) | **Case Study B (Shell-Packed 4-Tube)** |
| :--- | :---: | :---: | :---: | :---: |
| **Shell Diameter ($D_{\text{shell}}$)** | $11.28\text{ mm}$ | $20.00\text{ mm}$ | $19.88\text{ mm}$ | **$20.00\text{ mm}$** |
| **Membrane Area ($A_m$)** | $0.000\text{ m}^2$ | $0.0314\text{ m}^2$ | $0.0754\text{ m}^2$ | **$0.0628\text{ m}^2$** |
| **Specific Membrane Area ($a_v$)** | $0.0\text{ m}^{-1}$ | $133.33\text{ m}^{-1}$ | $754.0\text{ m}^{-1}$ | **$266.67\text{ m}^{-1}$** |
| **Void / Inert Fraction** | $0.0\%$ | $0.0\%$ | $31.37\%$ (must seal) | **$0.0\%$ (Zero Voids)** |
| **$\text{CO}_2$ Conversion ($X_{\text{CO}_2}$)** | $34.90\%$ | $93.62\%$ | $96.19\%$ | **$96.26\%$** |
| **DME Yield ($Y_{\text{DME}}$)** | $31.17\%$ | $91.94\%$ | $92.39\%$ | **$94.28\%$** |
| **DME Selectivity ($S_{\text{DME}}$)** | $89.29\%$ | $98.21\%$ | $96.05\%$ | **$97.94\%$** |
| **$\text{H}_2\text{O}$ Removal Ratio** | $0.00\%$ | $99.11\%$ | $99.75\%$ | **$99.70\%$** |
| **Carbon Balance Error** | $5.94 \times 10^{-16}$ | $< 1.0 \times 10^{-15}$ | $7.00 \times 10^{-16}$ | **$7.43 \times 10^{-16}$** |

![Shell-Packed 3D Cutaway](figures/dme_shell_packed_3d_cutaway.png)

---

## 5. Visual Schematics & Architectural Figures

* **Shell-Packed 2D Cross-Section (Case Study B):** [figures/dme_shell_packed_cross_section.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_shell_packed_cross_section.png)
* **Shell-Packed 3D Cutaway Diagram (Case Study B):** [figures/dme_shell_packed_3d_cutaway.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_shell_packed_3d_cutaway.png)
* **Sleeve Bundle 2D Cross-Section (Case Study A):** [figures/dme_bundle_sleeve_cross_section.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_bundle_sleeve_cross_section.png)
* **Sleeve Bundle 3D Cutaway Diagram (Case Study A):** [figures/dme_bundle_3d_cutaway.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_bundle_3d_cutaway.png)
* **Parametric Yield vs. Thickness & Diameter:** [figures/dme_yield_vs_thickness.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_yield_vs_thickness.png)
* **Multi-Architecture Benchmark Chart:** [figures/dme_layout_comparison.png](file:///Users/sameershekhar/Documents/GitHub/p1/figures/dme_layout_comparison.png)

---

## 6. Summary Findings & Engineering Guidelines

1. **Intensification Exceeds Gibbs Ceiling:** Continuous water removal via hydrophilic zeolite NaA membranes elevates single-pass $\text{CO}_2$ conversion from **$34.90\%$ to $96.19\%$** and DME yield from **$31.17\%$ to $92.39\%$**, surpassing the thermodynamic equilibrium limit ($48.71\%$) by **$+47.48\text{ percentage points}$**.
2. **Superiority of Uniform Catalyst Sleeves:** Wrapping each tube in a uniform sleeve ($t = 1.12\text{--}1.50\text{ mm}$) guarantees that no catalyst pellet is more than distance $t$ from a membrane surface, eliminating the stagnant corner zones characteristic of conventional shell-packed bundles.
3. **Void Sealing is Mandatory:** Unsealed interstitial voids result in up to **$31.4\%$ bypass channeling**, penalizing DME yield by **$-29.66\text{ percentage points}$** ($92.39\% \to 62.73\%$).
4. **Recommended Industrial Sizing:** Sizing at **$t = 1.50\text{ mm}$** ($d = 6.0\text{ mm}, d_s = 9.0\text{ mm}, D = 21.7\text{ mm}, L = 0.71\text{ m}$) resolves the fine-pellet packing limit ($t/d_p \ge 5.0$), avoiding wall channeling while achieving **$93.84\%$ DME yield** and **$97.56\%$ DME selectivity**.
