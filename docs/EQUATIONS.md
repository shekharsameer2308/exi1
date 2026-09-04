# Governing Equations and Parameter Definitions

**Framework**: 1D Non-Isothermal Plug Flow Membrane Reactor (E-Methanol Synthesis)  
**Implementation Location**: `src/emethanol/`  

---

## 1. Species Mass Balances
For each chemical species $i \in \{\text{CO}_2, \text{H}_2, \text{CO}, \text{CH}_3\text{OH}, \text{H}_2\text{O}\}$:
$$\frac{dF_i}{dz} = \rho_{\text{cat}} A_{\text{cs}} \sum_{j=1}^{N_{\text{rxn}}} \nu_{ij} r_j - a_{\text{mem}} J_i$$
where:
- $F_i(z)$: Molar flow rate of species $i$ $[\text{mol/s}]$
- $\rho_{\text{cat}}$: Catalyst bed density $[1100.0\text{ kg/m}^3]$
- $A_{\text{cs}} = \frac{\pi D^2}{4}$: Bed cross-sectional area $[\text{m}^2]$
- $a_{\text{mem}} = \pi D$: Membrane perimeter per unit length $[\text{m}]$
- $\nu_{ij}$: Stoichiometric coefficient of species $i$ in reaction $j$
- $r_j$: Reaction rate of reaction $j$ $[\text{mol}/(\text{kg}_{\text{cat}}\cdot\text{s})]$
- $J_i$: Radial membrane permeation flux $[\text{mol}/(\text{m}^2\cdot\text{s})]$

---

## 2. Reaction Stoichiometry & Kinetics

### Reaction 1: Direct $\text{CO}_2$ Hydrogenation to Methanol
$$\text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O} \quad (\Delta H^\circ_{298} = -49.5\text{ kJ/mol})$$

### Reaction 2: Reverse Water-Gas Shift (RWGS)
$$\text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O} \quad (\Delta H^\circ_{298} = +41.2\text{ kJ/mol})$$

### Vanden Bussche & Froment (1996) LHHW Formulation
$$r_{\text{MeOH}} = \frac{k_{5a} p_{\text{CO}_2} p_{\text{H}_2} \left(1 - \frac{p_{\text{MeOH}} p_{\text{H}_2\text{O}}}{K_{\text{eq},1} p_{\text{CO}_2} p_{\text{H}_2}^3}\right)}{\text{Denom}^3}$$

$$r_{\text{RWGS}} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left(1 - \frac{p_{\text{CO}} p_{\text{H}_2\text{O}}}{K_{\text{eq},3} p_{\text{CO}_2} p_{\text{H}_2}}\right)}{\text{Denom}}$$

$$\text{Denom} = 1 + K_{\text{H}_2\text{O}/K_{\text{H}_2}^{0.5}} \frac{p_{\text{H}_2\text{O}}}{\sqrt{p_{\text{H}_2}}} + K_{\text{H}_2}^{0.5} \sqrt{p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}$$

---

## 3. Membrane Transport Equations

### Linear Driving Force (LDF) Model
$$J_i = Q_i (p_{\text{tube},i} - p_{\text{sweep},i}) \times 10^5 \quad [\text{mol}/(\text{m}^2\cdot\text{s})]$$
where $Q_{\text{H}_2\text{O}} = Q_0 \exp\left(-\frac{E_a}{R}\left(\frac{1}{T} - \frac{1}{T_{\text{ref}}}\right)\right)$ and $Q_i = Q_{\text{H}_2\text{O}} / \alpha_{i}$.

---

## 4. Non-Isothermal Energy Balance
$$\frac{dT}{dz} = \frac{\rho_{\text{cat}} A_{\text{cs}} \left[ (-\Delta H_{\text{rxn},1}) r_{\text{MeOH}} + (-\Delta H_{\text{rxn},2}) r_{\text{RWGS}} \right] - U \pi D (T - T_{\text{cool}})}{\sum_{i=1}^5 F_i C_{p,i}(T)}$$

---

## 5. Momentum Balance (Ergun Equation)
$$\frac{dP}{dz} = -\left[ 150 \frac{(1-\epsilon)^2}{\epsilon^3} \frac{\mu u_s}{d_p^2} + 1.75 \frac{1-\epsilon}{\epsilon^3} \frac{\rho_{\text{gas}} u_s^2}{d_p} \right] \times 10^{-5} \quad [\text{bar/m}]$$
where $u_s = \frac{F_{\text{tot}} R T}{P A_{\text{cs}}}$ is superficial gas velocity.

---

## 6. Physical Parameter Reference Table

| Parameter | Symbol | Value | Unit | Source |
|---|---|---|---|---|
| Universal Gas Constant | $R$ | 8.31446 | $\text{J/(mol}\cdot\text{K)}$ | CODATA |
| Catalyst Density | $\rho_{\text{cat}}$ | 1100.0 | $\text{kg/m}^3$ | Commercial CZA |
| Bed Void Fraction | $\epsilon$ | 0.40 | - | Standard packed bed |
| Pellet Diameter | $d_p$ | 0.002 | $\text{m}$ | Industrial tablet |
| Heat Transfer Coeff | $U$ | 50.0 | $\text{W/(m}^2\cdot\text{K)}$ | Wall cooled tube |
| Base H2O Permeance | $Q_{\text{H}_2\text{O}}$ | $1.0\times 10^{-7}$ | $\text{mol/(m}^2\cdot\text{s}\cdot\text{Pa)}$ | Energy Advances (2025) |
