# Membrane Reactor Full Analytical Results

This document presents the detailed execution results of the 1D steady-state co-current model across both reactor modules, followed by a comprehensive data-driven contour and surrogate model analysis.

## 1. Module B (Ammonia Decomposition)
**Architecture:** Catalyst packed inside the **lumen**, Pd membrane wrapper, H₂ permeating outward.

### Performance Data
| Operating Case | TR Conversion (%) | MR Conversion (%) | Absolute Gain (pp) | H₂ Recovery Factor (HRF %) |
|----------------|:---:|:---:|:---:|:---:|
| **Ammonia Decomposition Base** | 81.06 | 81.29 | +0.23 | 2.04 |
| **Jiang 2021 Target** | 81.06 | 84.42 | +3.36 | 26.16 |


**Visual Architecture:**
![Module B Cross Section](figures/2d_cross_section_module_b.png)
![Module B 3D Cutaway](figures/3d_cutaway_module_b.png)

---

## 2. Module A (CO₂ Hydrogenation)
**Architecture:** Catalyst packed in the **annulus**, Zeolite NaA membrane in the center, H₂O permeating inward.

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

## 3. Detailed Process Profiles (Original Reactor Model)
The following profiles detail the internal reaction-diffusion behavior across the reactor length.

### Axial Temperature & Reaction
![Temperature Profile](results/figures/01_temperature_profile.png)
![Reaction Rates](results/figures/03_reaction_rates.png)

### Species & Permeation
![Species Profiles](results/figures/02_species_profiles.png)
![Membrane Flux](results/figures/04_membrane_flux.png)
![H2O Removal](results/figures/05_h2o_removal.png)

---

## 4. Intensification Maps & Contours
The surrogate modeling maps reveal the multidimensional operating landscape for the membrane reactor.

### Operating Sensitivity
![Temp vs Pressure](results/figures/06_temperature_pressure_map.png)
![Temp vs GHSV](results/figures/07_temperature_gHSV_map.png)
![Pressure vs Sweep-to-Feed (S/F)](results/figures/08_pressure_SF_map.png)

### Membrane Area (O_m / V_r) Effects
![Membrane Area Map](results/figures/09_membrane_area_map.png)

### Final Contour Maps
![Conversion Contour](results/figures/10_conversion_contour.png)
![Methanol Yield Contour](results/figures/11_methanol_yield_contour.png)
![Optimization Landscape](results/figures/15_optimization_landscape.png)

---

## 5. Surrogate Machine Learning Performance
A Random Forest surrogate was trained on a Design of Experiments (DOE) grid to map the physics parameter space to the conversion gains.

![Feature Importance](results/figures/14_feature_importance.png)
![Surrogate Parity](results/figures/12_surrogate_parity.png)
![Surrogate Residuals](results/figures/13_surrogate_residuals.png)
