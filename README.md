# Intensified Catalytic Membrane Reactor (CMR) for E-Methanol Synthesis

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A scientific computing and machine learning framework for simulating, designing, and optimizing an intensified catalytic membrane reactor for synthetic e-methanol production via $\text{CO}_2$ hydrogenation. The system couples 2D heterogeneous mass and heat transport with the coupled Maxwell-Stefan multicomponent permeation formulation established by **Hauth et al. (2025)** and utilizes Grey-Box Neural Ordinary Differential Equations (Neural ODEs) to accelerate computational convergence.

```
                      ANNULAR CATALYTIC REACTION ZONE (Retentate: 100 bar, 250 °C)
    +-------------------------------------------------------------------------------------------------+
    | Feed Gas ----> Catalyst Bed: Cu/ZnO/Al2O3 Pellets (CO2 + 3H2 -> CH3OH) ----> High-Yield Retentate|
    +-------------------------------------------------------------------------------------------------+
    | = = = = = = = = = = = = = = = = = NaA ZEOLITE MEMBRANE INTERFACE = = = = = = = = = = = = = = =  |
    |               | In-Situ Steam Permeation Flux (Coupled Maxwell-Stefan)                          |
    |               v                                                                                 |
    +-------------------------------------------------------------------------------------------------+
    | Sweep Gas <--- Permeate Extraction Channel (Sweep Gas: N2 or Steam at 1 bar) <--- Sweep Feed In |
    +-------------------------------------------------------------------------------------------------+
```

---

## 1. Process Intensification Physics

In conventional fixed-bed reactors, methanol synthesis from $\text{CO}_2$ and $\text{H}_2$ is severely equilibrium-limited, yielding only $15\% - 22\%$ conversion per pass at industrial pressures ($50 - 100\text{ bar}$) and temperatures ($220 - 250\text{ °C}$). This necessitates massive recycle streams with recycle ratios exceeding $4.0 - 6.0$, driving up compressor energy demand.

The catalytic membrane reactor (CMR) breaks this thermodynamic barrier by continuously extracting water vapor from the reaction zone through a permselective zeolite membrane.

- **Le Chatelier Equilibrium Shift**: Continuous extraction of steam removes a primary reaction product, driving both methanol synthesis and reverse water-gas shift (RWGS) forward, lifting the single-pass conversion ceiling beyond $50\%$.
- **Mitigating Permeation Bottlenecks**: At standard tube dimensions (e.g., $d_w = 40\text{ mm}$, $O_M/V_r = 26.67\text{ m}^{-1}$), radial concentration polarization limits steam removal to less than $8\%$, rendering the membrane ineffective ($+0.3\%$ conversion gain). Increasing the membrane area-to-volume ratio to $O_M/V_r = 133.33\text{ m}^{-1}$ ($d_w = 20\text{ mm}$ around a $10\text{ mm}$ core) narrows the radial diffusion path to $5\text{ mm}$, driving water extraction up to $88.1\%$.
- **Operating Temperature Threshold**: Methanol permeation drops sharply above its critical temperature ($T_c = 239.9\text{ °C}$) due to the loss of capillary condensation inside the micropores. Operating at $250\text{ °C}$ ensures near-zero methanol loss, yielding high $\text{H}_2\text{O}/\text{CH}_3\text{OH}$ selectivity without relying on molecular sieving alone.
- **Catalyst Protection Boundary**: Commercial $\text{Cu/ZnO/Al}_2\text{O}_3$ requires a minimum partial pressure of steam ($p_{\text{H}_2\text{O}} \ge 0.015 \cdot P_{\text{total}}$, or $1.5\text{ bar}$ at $100\text{ bar}$) to prevent over-reduction of active $\text{Cu}^+$ sites to inactive metallic brass ($\alpha\text{-CuZn}$). Water removal is strictly regulated to keep exit partial pressure above this limit.

---

## 2. Governing Equations

### 2.1 Chemical Reaction Kinetics
The reaction network includes competitive $\text{CO}_2$ hydrogenation and the reverse water-gas shift (RWGS) reaction over $\text{Cu/ZnO/Al}_2\text{O}_3$, modeled using the Mignard and Pritchard formulation:

$$\text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O} \qquad \Delta H_{298\text{ K}}^\circ = -49.5 \text{ kJ}\cdot\text{mol}^{-1}$$

$$\text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O} \qquad \Delta H_{298\text{ K}}^\circ = +41.2 \text{ kJ}\cdot\text{mol}^{-1}$$

The reaction rate expressions are defined as:

$$r_{\text{MeOH}} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left(1 - \dfrac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{K_{\text{eq},1} p_{\text{H}_2}^3 p_{\text{CO}_2}}\right)}{\left(1 + K_{\text{H}_2\text{O}/\text{H}_2}\dfrac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}} + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}\right)^3}$$

$$r_{\text{RWGS}} = \frac{k_2 p_{\text{CO}_2} \left(1 - \dfrac{p_{\text{H}_2\text{O}} p_{\text{CO}}}{K_{\text{eq},2} p_{\text{H}_2} p_{\text{CO}_2}}\right)}{1 + K_{\text{H}_2\text{O}/\text{H}_2}\dfrac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}} + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}}$$

Equilibrium constants are determined by Graaf's thermodynamic correlations:

$$\log_{10} K_{\text{eq},1} = \frac{3066}{T} - 10.592 \quad [\text{bar}^{-2}], \qquad \log_{10} K_{\text{eq},2} = -\frac{2073}{T} + 2.029 \quad [-]$$

### 2.2 Coupled Maxwell-Stefan Multicomponent Permeation
Permeation across the microporous zeolite membrane is described by the coupled Maxwell-Stefan matrix equations, capturing competitive adsorption, correlation effects, and molecular slowing:

$$\mathbf{J} = -\rho_m [q_{\text{sat}}] [B]^{-1} [\Gamma] \frac{d\boldsymbol{\theta}}{dr}$$

Multicomponent Langmuir Adsorption:

$$\theta_i = \frac{b_i p_i}{1 + \sum_{j} b_j p_j}, \qquad \theta_v = 1 - \sum_{i} \theta_i$$

$$b_i(T) = b_{0,i} \exp\left(-\frac{\Delta H_{\text{ads},i}}{RT}\right)$$

Thermodynamic Correction Matrix $[\Gamma]$:

$$\Gamma_{ij} = \delta_{ij} + \frac{\theta_i}{\theta_v}$$

Maxwell-Stefan Friction Matrix $[B]$:

$$B_{ii} = \frac{1}{D_i} + \sum_{j \neq i} \frac{\theta_j}{D_{ij}}, \qquad B_{ij} = -\frac{\theta_i}{D_{ij}}$$

Temperature-Dependent Diffusivities:

$$D_i(T) = D_{0,i} \exp\left(-\frac{E_{A,i}}{RT}\right)$$

The exchange diffusivity between water and methanol is explicitly accounted for as $D_{\text{H}_2\text{O},\text{CH}_3\text{OH}} = 3.0 \times 10^{-9}\text{ m}^2/\text{s}$.

### 2.3 2D Heterogeneous Packed-Bed Balances
The continuous annular reaction domain ($r \in [r_m, r_w]$, $z \in [0, L]$) is governed by coupled 2D partial differential equations:

Species Differential Mass Balance:

$$u_s(z) \frac{\partial C_i}{\partial z} = D_{er} \left( \frac{\partial^2 C_i}{\partial r^2} + \frac{1}{r} \frac{\partial C_i}{\partial r} \right) + \rho_b \eta_i \sum_{j} \nu_{ij} r_j$$

Non-Isothermal Energy Balance:

$$u_s(z) \rho_g C_{p,g} \frac{\partial T}{\partial z} = \lambda_{er} \left( \frac{\partial^2 T}{\partial r^2} + \frac{1}{r} \frac{\partial T}{\partial r} \right) + \rho_b \sum_{j} (-\Delta H_j) r_j$$

Membrane Wall Boundary Conditions ($r = r_m$):

$$-D_{er} \left.\frac{\partial C_i}{\partial r}\right\vert_{r=r_m} = J_i(\mathbf{p}, T)$$

$$-\lambda_{er} \left.\frac{\partial T}{\partial r}\right\vert_{r=r_m} = \sum_{i} J_i \left[ \Delta H_{\text{des},i} + C_{p,i}(T - T_{\text{perm}}) \right]$$

Dynamic Ergun Momentum Balance:

$$\frac{dP}{dz} = -\left[ 150 \frac{\mu(1-\epsilon)^2}{d_p^2 \epsilon^3} u_s(z) + 1.75 \frac{\rho_g(1-\epsilon)}{d_p \epsilon^3} u_s(z)^2 \right], \qquad u_s(z) = \frac{\sum F_{i,\text{ret}}(z) \cdot R \cdot T(z)}{P(z) \cdot A_c}$$

---

## 3. Scientific Machine Learning (SciML) Architecture

```
       [ Input States: p_i, T, Delta_p ]
                       |
                       v
       +-------------------------------+
       | Hard Physics Convection-      | ---> Stoichiometric Conservation & Kinetics
       | Dispersion Conservation       |      (Mignard & Pritchard Equations)
       +-------------------------------+
                       |
       +---------------+---------------+
       |                               |
       v                               v
+-------------------------------+ +-------------------------------+
| Mechanistic Solver Path       | | SciML Hybrid Neural ODE       |
| Explicit Inversion:           | | Forward Bypass:               |
| J = -rho_m [q_sat] [B]^-1...  | | J_pred = NN_phi(p, T, dp)     |
+-------------------------------+ +-------------------------------+
       |                               |
       +---------------+---------------+
                       |
                       v
       [ Output: Coupled Axial Flux Profiles ]
```

- **The Computational Problem**: Inverting the stiff $3 \times 3$ Maxwell-Stefan matrix $[B]$ at every grid point within a stiff 2D PDE solver creates significant computational overhead, making real-time control and high-throughput multi-objective optimization impractical.
- **Hybrid Grey-Box Formulation**: Convection, radial dispersion, and catalytic reaction terms remain strictly hardcoded in the solver. A multi-layer perceptron $\mathbf{NN}_{\phi}(\mathbf{p}, T, \Delta p)$ is trained directly on high-fidelity CFD solution meshes to infer the membrane flux vector $\mathbf{J}$ directly:
  $$\frac{d\mathbf{C}}{dz} = \mathbf{f}_{\text{physics}}(\mathbf{C}, T) - \frac{4 d_m}{d_w^2 - d_m^2} \cdot \mathbf{NN}_{\phi}(\mathbf{p}, T, \Delta p)$$
- **Physical Inductive Biases**: The surrogate network uses bounded Sigmoid and positive-ReLU activations to prevent negative mass predictions and ensure zero flux under zero partial pressure.
- **Multi-Objective Bayesian Optimization**: The BoTorch framework uses Gaussian Process surrogates to find optimal tradeoffs between Space-Time Yield ($\text{STY}$) and Specific Energy Consumption ($\text{kWh}/\text{kg}_{\text{MeOH}}$) while accounting for sweep recycle penalties.

---

## 4. Benchmark Validation & CFD Target Metrics

The simulation core is validated against the 3D CFD data reported by **Hauth et al. (2025)**. The test case models a $250\text{ mm}$ reactor tube operating at $250\text{ °C}$ and $100\text{ bar}$ retentate pressure:

| Metric | Conventional Fixed Bed (TR) | Intensified Membrane (MR) | Reference Status |
| :--- | :--- | :--- | :--- |
| **Reactor Geometry** | $d_w = 20\text{ mm}, L = 0.25\text{ m}$ | $d_w = 20\text{ mm}, d_m = 10\text{ mm}, L = 0.25\text{ m}$ | Annular gap: $5\text{ mm}$ ($O_M/V_r = 133.3\text{ m}^{-1}$) |
| **Space Velocity (GHSV)** | $500\text{ h}^{-1}$ ($\dot{V} = 0.49\text{ L/min}$) | $500\text{ h}^{-1}$ (Sweep-to-feed $S/F = 10$) | Matched inlet flow conditions |
| **Pressure Difference ($\Delta p$)** | $0.0\text{ bar}$ | $99.0\text{ bar}$ ($P_{\text{perm}} = 1.0\text{ bar}$) | Maximum extraction driving force |
| **Single-Pass $\text{CO}_2$ Conversion** | **$31.42\%$** | **$52.08\%$** | **$+20.66\%$ absolute gain** |
| **Single-Pass $\text{CH}_3\text{OH}$ Yield** | **$25.71\%$** | **$40.48\%$** | **$+14.77\%$ absolute gain** |
| **In-Situ $\text{H}_2\text{O}$ Removal** | **$0.00\%$** | **$88.10\%$** | Verified equilibrium shift |
| **Retentate Exit $p_{\text{H}_2\text{O}}$** | **$4.85\text{ bar}$** | **$2.85\text{ bar}$** | Above critical limit ($> 1.50\text{ bar}$) |
| **Recycle Compression Reduction** | Baseline ($0.0\%$) | $\approx 20\%$ reduction ($1/5$) | Decreased unreacted recycle volume |

---

## 5. Quickstart & Reproducibility

### Installation
Clone the repository and set up the Conda environment:

```bash
git clone https://github.com/shekharsameer2308/exi1.git membrane-reactor-sciml
cd membrane-reactor-sciml

# Create and activate environment
conda env create -f environment.yml
conda activate membrane-sciml

# Install package in editable mode with development tools
pip install -e .
```

### Reproducing Benchmark Targets
Run the self-contained verification benchmark to reproduce the results from Hauth et al. (2025):

```bash
python benchmark_run.py
```

Expected terminal output:
```text
====================================================================
 RIGOROUS MAXWELL-STEFAN VERIFICATION AUDIT (HAUTH ET AL., 2025)
====================================================================
Condition: T = 250 °C, P = 100 bar, delta_p = 99 bar, OM/Vr = 133.3 m^-1
--------------------------------------------------------------------
Conventional Fixed Bed (TR) : CO2 Conv = 31.42%, MeOH Yield = 25.71%
Intensified Membrane   (MR) : CO2 Conv = 52.08%, MeOH Yield = 40.48%
H2O Extraction Achieved     : 88.10%
Retentate Exit p_H2O        : 2.85 bar (Threshold >= 1.50 bar)
Absolute Performance Boost  : +20.66% Conv, +14.77% Yield
====================================================================
```

### Running the Test Suite
Run tests to verify physical laws (conservation of atoms, Onsager symmetry) and integration routines:

```bash
pytest tests/ -v
```

### Multi-Objective Optimization & Dashboards
To run the Bayesian optimization loop and generate the 4-panel diagnostic dashboard:

```bash
python ml/bayesian_opt.py --trials 50
python visualization/dashboard.py
```

Generated plots will be saved to `reports/figures/reactor_intensification_dashboard.png`.
