# Model Description & Scientific Reference Alignment

**Primary Reference**:  
*"Design parameter optimization of a membrane reactor for methanol synthesis using a sophisticated CFD model"*, *Energy Advances* (2025).

---

## 1. Model Level Classification Hierarchy

To maintain scientific integrity and prevent unjustified equivalency claims, the physics representations within this repository are explicitly classified into four distinct levels:

```
┌────────────────────────────────────────────────────────┐
│  LEVEL 4: 2D / 3D Computational Fluid Dynamics (CFD)   │
│  • Full Navier-Stokes + Multicomponent species CFD     │
│  • 3D radial and axial boundary layer gradients        │
│  • Local thermal hotspot & fluid flow distribution     │
├────────────────────────────────────────────────────────┤
│  LEVEL 3: Reference-Aligned 1D Transport Model         │
│  • Mignard & Pritchard (2008) VBF modification kinetics│
│  • Coupled Maxwell-Stefan multicomponent zeolite flux  │
│  • Counter-current sweep-side species mass balance     │
├────────────────────────────────────────────────────────┤
│  LEVEL 2: Enhanced 1D Non-Isothermal Membrane Reactor  │  ◄── [Core Framework Implementation]
│  • VBF (1996) + Mignard & Pritchard kinetics switch    │
│  • Non-isothermal energy balance: dT/dz = f(ΔH, U, Cp) │
│  • Temperature-dependent LDF H2O permeation            │
│  • Packed-bed pressure drop (Ergun equation)           │
│  • Automatic Carbon/Hydrogen/Oxygen conservation QC    │
├────────────────────────────────────────────────────────┤
│  LEVEL 1: Legacy Reduced-Order Reactor Baseline        │
│  • Isothermal, isobaric 1D ODE system                  │
│  • Simplified single-component H2O LDF permeation      │
│  • Constant sweep side assumption                      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Key Insights from the 2025 *Energy Advances* Reference

1. **Reactor Architecture**:
   - Concentric tube-in-tube configuration.
   - Inner reaction tube packed with commercial $\text{CuO/ZnO/Al}_2\text{O}_3$ (CZA) catalyst.
   - Hydrophilic $\text{NaA}$ zeolite membrane selective to water vapor removal.
   - Shell annulus for counter-current sweep gas flow ($\text{N}_2$ or recycled gas).

2. **Crucial Optimization Parameters**:
   - **GHSV** (Gas Hourly Space Velocity, $\text{h}^{-1}$): Balances contact time and residence time against throughput.
   - **Sweep/Feed Ratio ($S/F$)**: Controls sweep-side driving force and water partial pressure buildup.
   - **Membrane Area to Reaction Volume Ratio ($A_{\text{mem}}/V_{\text{rxn}}$)**: Dictates total permeation capacity per unit catalyst volume.
   - **Operating Temperature and Pressure**: Trade-off between fast forward kinetics at high $T$ vs thermodynamic equilibrium limitation (Le Chatelier's principle) favoring lower $T$ and higher $P$.

3. **Membrane Effectiveness Nuance**:
   - As noted in the reference paper, baseline membrane configurations without parameter optimization achieve modest water removal ($\sim 7.82\%$).
   - High performance requires coordinated optimization of $S/F$, membrane area ratio, and space velocity.

---

## 3. Kinetic Models Supported

### A. Original Vanden Bussche & Froment (1996)
- Designed for commercial $\text{Cu/ZnO/Al}_2\text{O}_3$ catalyst.
- Accounts for $\text{CO}_2$ as primary carbon source for methanol synthesis, with RWGS side-reaction producing $\text{CO}$.

### B. Mignard & Pritchard (2008) Modification
- Recalibrated activation energies and equilibrium formulations specifically suited for elevated $\text{CO}_2$ concentrations in e-methanol feedstocks.
