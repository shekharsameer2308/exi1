# Full-Length Industrial Reactor Design & Multi-Tubular Scale-Up

**Module**: `src/emethanol/design.py`  
**API**: `design_full_length_reactor(...)`  

---

## 1. Multi-Tubular Membrane Reactor Architecture

For industrial e-methanol synthesis, commercial tube-in-tube catalytic membrane reactors utilize high aspect ratio tubes ($L = 3.0 - 6.0\text{ m}$, $D_t = 25 - 38\text{ mm}$) arranged in a shell-and-tube bundle:

```
                  ◄── BOILING WATER / COOLANT OUTLET (Steam Generation)
        ┌────────────────────────────────────────────────────────┐
        │  SHELL: Counter-Current Sweep Gas (N2) / Shell Coolant │
  ──────┤ ┌────────────────────────────────────────────────────┐ ├──────
  FEED  │ │ ====== Hydrophilic NaA Membrane Tube Wall ======   │ │ PROD
  GAS   │ │                                                    │ │ OUT
  (CO2  │ │   CATALYST BED: CuO/ZnO/Al2O3 (CZA Pellets)        │ │ (MeOH,
  + H2) │ │   CO2 + 3H2 ⇌ CH3OH + H2O (Exothermic)             │ │ CO,
  ─────►│ │   CO2 + H2 ⇌ CO + H2O (RWGS)                       │ │ H2O)
        │ │   Radial Permeation: ↓↓↓ H2O Extraction ↓↓↓        │ │─────►
  ──────┤ └────────────────────────────────────────────────────┘ ├──────
        │  SHELL ANNULUS (Sweep + Extracted Steam)               │
        └────────────────────────────────────────────────────────┘
                  ──► SWEEP GAS INLET (N2) / COOLANT INLET
```

---

## 2. Scale-Up & Sizing Equations

### Number of Parallel Tubes ($N_{\text{tubes}}$)
Given a target plant capacity $\dot{M}_{\text{target}}$ [Metric Tons/Day (TPD)]:
$$N_{\text{tubes}} = \left\lceil \frac{\dot{M}_{\text{target}}}{\dot{m}_{\text{MeOH,tube}}} \right\rceil$$
where single tube production is:
$$\dot{m}_{\text{MeOH,tube}} = F_{\text{out,MeOH}} \times M_{\text{MeOH}} \times 10^{-3} \times 86400 \times 10^{-3} \quad [\text{TPD/tube}]$$

### Catalyst Mass & Membrane Area
$$W_{\text{cat,total}} = N_{\text{tubes}} \left( \rho_{\text{cat}} \frac{\pi D_t^2}{4} L \right) \quad [\text{kg}]$$
$$A_{\text{mem,total}} = N_{\text{tubes}} (\pi D_t L) \quad [\text{m}^2]$$
$$\left( \frac{A_{\text{mem}}}{V_{\text{rxn}}} \right) = \frac{4}{D_t} \quad [\text{m}^2/\text{m}^3]$$

### Shell Diameter (Triangular Tube Pitch Array)
With pitch $p_t = 1.35 D_o$:
$$D_{\text{shell}} = 1.15 \times \sqrt{\frac{4 N_{\text{tubes}} (0.866 p_t^2)}{\pi}} \quad [\text{m}]$$

### Space Velocities
$$\text{GHSV} = \frac{\dot{V}_{\text{feed,STP}}}{V_{\text{bed,total}}} \quad [\text{h}^{-1}], \qquad \text{WHSV} = \frac{\dot{m}_{\text{feed}}}{W_{\text{cat,total}}} \quad [\text{h}^{-1}]$$

---

## 3. Commercial Design Reference Case (100 TPD Methanol)

| Design Parameter | Bench Scale ($L=1.0\text{ m}$) | Pilot Scale ($L=3.0\text{ m}$) | Commercial Plant ($L=6.0\text{ m}$) |
|---|---|---|---|
| **Target Capacity** | 0.1 kg/day | 1.0 TPD | **100.0 TPD** |
| **Tube Length ($L$)** | 1.0 m | 3.0 m | **6.0 m** |
| **Tube Diameter ($D_t$)** | 20 mm | 25 mm | **38 mm** |
| **Number of Tubes ($N_t$)** | 1 tube | 32 tubes | **1,500 tubes** |
| **Shell Diameter** | 0.05 m | 0.35 m | **2.2 m** |
| **Total Catalyst Mass** | 0.35 kg | 52 kg | **11.2 Metric Tons** |
| **Total Membrane Area** | 0.063 m² | 7.5 m² | **1,074 m²** |
| **$\text{CO}_2$ Consumption** | 0.15 kg/day | 1.45 TPD | **142.5 TPD** |
| **Green $\text{H}_2$ Required** | 0.02 kg/day | 0.20 TPD | **19.8 TPD** |
| **Electrolyzer Power** | 0.05 kW | 0.45 MW | **45.3 $\text{MW}_{\text{el}}$** |
| **Reaction Cooling Duty** | 0.02 kW | 22 kW | **2.15 $\text{MW}_{\text{thermal}}$** |
| **Water Extracted** | 0.05 kg/day | 0.54 TPD | **53.4 TPD** |
| **Bed Pressure Drop** | 0.01 bar | 0.35 bar | **1.25 bar** |
