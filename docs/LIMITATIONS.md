# Known Physical and Transport Limitations

**Framework**: E-Methanol Packed-Bed Membrane Reactor Platform  

---

## 1. Dimensionality & Fluid Dynamics Limitations
1. **Absence of Radial Boundary Layers**: The model is 1D axial plug flow; it does not resolve radial velocity profiles, boundary layer mass transfer resistance adjacent to the membrane surface, or radial temperature profiles across the packed bed.
2. **Turbulence and Recirculation**: No Navier-Stokes fluid turbulence modeling (as present in 3D CFD Fluent models).

---

## 2. Membrane & Transport Limitations
1. **Simplified Permeate Side Hydrodynamics**: Sweep side is modeled as a dilute counter-current sink; radial sweep concentration polarization is neglected.
2. **Coupled Zeolite Diffusion Parameters**: While the Maxwell-Stefan framework is fully formulated, binary Maxwell-Stefan interaction parameters for ternary gas mixtures in microporous NaA zeolite under high-pressure conditions remain scarce in the literature and require experimental pervaporation / permeation measurement.

---

## 3. Catalyst Deactivation
1. Current kinetics assume fresh commercial $\text{CuO/ZnO/Al}_2\text{O}_3$ catalyst activity ($a = 1.0$); long-term thermal sintering, carbon deposition, and water-induced hydrothermal deactivation are not modeled dynamically.
