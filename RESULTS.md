# Membrane Reactor Optimization Results

This document presents the detailed execution results of the 1D steady-state co-current model across both reactor modules.

## Module B (Ammonia Decomposition - Catalyst in Lumen)
As highlighted by Sitar et al. (2022), the decomposition of ammonia is highly endothermic and limited by equilibrium. The architecture utilizes a **Pd membrane on a Ru/YSZ support**, with the **catalyst packed bed inside the lumen region**. 

- **Feed:** Pure NH₃ enters the central lumen.
- **Permeate:** Hydrogen selectively permeates outward through the Pd membrane into the sweep/shell side.
- **Retentate:** N₂ and residual unreacted NH₃ exit the lumen.

### Performance Data
| Operating Case | TR Conversion (%) | MR Conversion (%) | Absolute Gain (pp) | H₂ Recovery Factor (HRF %) |
|----------------|:---:|:---:|:---:|:---:|
| **Ammonia Decomposition Base** | 81.06 | 81.29 | +0.23 | 2.04 |
| **Jiang 2021 Target** | 81.06 | 84.42 | +3.36 | 26.16 |


**Visual Architecture:**
![Module B Cross Section](figures/2d_cross_section_module_b.png)
![Module B 3D Cutaway](figures/3d_cutaway_module_b.png)

---

## Module A (CO₂ Hydrogenation - Catalyst in Annulus)
CO₂ hydrogenation to e-methanol operates in a tube-in-tube configuration with the **catalyst in the annulus** and a **Zeolite NaA water-selective membrane**.

### Performance Data
| Operating Case | TR Conversion (%) | MR Conversion (%) | Absolute Gain (pp) | Water Removal (%) |
|----------------|:---:|:---:|:---:|:---:|
| **Base Case** | 30.59 | 30.80 | +0.21 | 2.06 |
| **GHSV 500** | 33.54 | 35.81 | +2.28 | 18.54 |
| **High Area** | 30.61 | 31.64 | +1.03 | 9.41 |
| **Fast Sweep** | 30.59 | 30.80 | +0.21 | 2.08 |
| **Best Case (Fig 12 Discrepancy)** | 33.52 | 44.54 | +11.02 | 60.70 |
| **Best Case (Text Discrepancy)** | 33.54 | 36.02 | +2.48 | 20.06 |
| **Best Case + dP 99 bar** | 33.52 | 45.10 | +11.58 | 62.48 |


**Visual Architecture:**
![Module A Cross Section](figures/2d_cross_section_module_a.png)
![Module A 3D Cutaway](figures/3d_cutaway_module_a.png)

---

### Mass Balance Integrity
The co-current numerical IVP formulation enforces strict mass conservation. Across all simulated nodes, the element balance closure (C, H, O, N) remains strictly below 0.1% error (observed Base Case error: `0.000000%`).