# 1D-Derived Pseudo-2D Reactor Performance Contours

**Module**: `src/emethanol/visualization.py`  
**Function**: `generate_reactor_contour(...)`  

---

## 1. Methodology & Physical Basis

> [!IMPORTANT]
> **Engineering Disclaimer**:
> These maps are **1D-derived pseudo-2D reactor performance contours**, NOT 2D/3D CFD Navier-Stokes solutions.

### Mathematical Formulation
A target scalar profile $\Phi(z)$ (such as $y_{\text{CH}_3\text{OH}}(z)$, $T(z)$, or $J_{\text{H}_2\text{O}}(z)$) is computed by repeatedly solving the 1D non-isothermal boundary-value ODE system across a discretized parametric range $\theta \in [\theta_{\min}, \theta_{\max}]$:
$$\mathbf{M}_{ij} = \Phi(z_j, \theta_i)$$
The resulting matrix $\mathbf{M} \in \mathbb{R}^{N_\theta \times N_z}$ is interpolated over a 2D mesh grid $(z, \theta)$ to produce spatial response surfaces:
- $X\text{-axis}$: Reactor length $z \in [0, L]$
- $Y\text{-axis}$: Swept operational parameter (Inlet $T$, Pressure $P$, Feed flow $F$, Permeance $Q$, or $\text{H}_2/\text{CO}_2$ ratio)
- $\text{Color Field}$: Local performance metric (Mole fraction, Local conversion, Local reaction rate, Permeation flux)
