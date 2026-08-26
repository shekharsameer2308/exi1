"""One-dimensional packed-bed and water-selective membrane-reactor model
for e-methanol synthesis from captured CO2 and green H2.

Kinetics: Vanden Bussche & Froment (1996), J. Catal. 161, 1-10.
          "A steady-state kinetic model for methanol synthesis and the
           water gas shift reaction on a commercial Cu/ZnO/Al2O3 catalyst."

Validated against: Slotboom et al. (2020), Chem. Eng. J. 389, 124181.
                   DOI 10.17632/fxwg9nbz2z.1

Reactions modelled
------------------
R1  CO2 + 3 H2  <=> CH3OH + H2O   (CO2 hydrogenation)
R2  CO2 + H2    <=> CO    + H2O   (reverse water-gas shift)

The CO hydrogenation (CO + 2H2 <=> CH3OH) is captured implicitly as the
linear combination R1 - R2 and is not given a separate rate expression in
the VBF formulation.

Units convention
----------------
  molar flows  : mol s-1
  temperature  : K
  pressure     : Pa  (user-facing config uses bar; 1 bar = 1e5 Pa)
  length       : m
  rates        : mol kgcat-1 s-1
  partial press: bar inside rate expressions (VBF convention)

Assumptions and limitations
---------------------------
* Pseudo-homogeneous 1-D plug-flow model; no radial gradients.
* Ideal-gas equation of state.
* Constant viscosity (mu = 2e-5 Pa s) for H2-rich mixtures.
* Reaction enthalpies are treated as approximately constant at 298 K values.
* Membrane flux follows Sieverts-type linear driving force.
* Catalyst activity is unity (no deactivation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np
from scipy.integrate import solve_ivp

# ---------------------------------------------------------------------------
# Physical constants and species data
# ---------------------------------------------------------------------------
R_GAS = 8.314462618          # J mol-1 K-1
SPECIES = ("CO2", "H2", "CO", "MeOH", "H2O", "N2")
NS = len(SPECIES)

# Molar masses [kg mol-1]
MW = {
    "CO2":  44.010e-3,
    "H2":    2.016e-3,
    "CO":   28.010e-3,
    "MeOH": 32.042e-3,
    "H2O":  18.015e-3,
    "N2":   28.014e-3,
}

# Shomate coefficients for ideal-gas Cp  [J mol-1 K-1]
# Source: NIST Chemistry WebBook, valid ~298-1200 K
# Cp = A + B*t + C*t^2 + D*t^3 + E/t^2,  t = T[K] / 1000
_SHOMATE = {
    #           A          B          C          D          E
    "CO2":  (24.99735,  55.18696, -33.69137,   7.948387, -0.136638),
    "H2":   (33.066178,-11.363417, 11.432816, -2.772874, -0.158558),
    "CO":   (25.56759,   6.09613,   4.054656, -2.671301,  0.131021),
    "MeOH": (14.818,   125.879,   -71.7095,   16.3478,   0.06858),
    "H2O":  (30.09200,   6.832514,  6.793435, -2.534480,  0.082139),
    "N2":   (28.98641,   1.853978, -9.647459,  16.63537,  0.000117),
}

# Stoichiometric matrix  [reaction x species]
# Row 0 = R1 (CO2 hydrogenation), Row 1 = R2 (RWGS)
#                CO2  H2  CO  MeOH H2O  N2
STOICH = np.array([
    [-1, -3,  0,  1,  1,  0],   # R1: CO2 + 3H2 -> CH3OH + H2O
    [-1, -1,  1,  0,  1,  0],   # R2: CO2 + H2  -> CO    + H2O
], dtype=float)

# Standard enthalpies of reaction at 298 K  [J mol-1]
DH_RXN = np.array([
    -49430.0,   # R1 exothermic
     41170.0,   # R2 endothermic (RWGS)
])


# ---------------------------------------------------------------------------
# Thermodynamic helpers
# ---------------------------------------------------------------------------
def _cp_shomate(species: str, T: float) -> float:
    """Ideal-gas molar heat capacity [J mol-1 K-1] via Shomate equation."""
    A, B, C, D, E = _SHOMATE[species]
    t = T / 1000.0
    return A + B * t + C * t**2 + D * t**3 + E / t**2


def _cp_mix(flows: np.ndarray, T: float) -> float:
    """Molar-average Cp of the gas mixture [J mol-1 K-1]."""
    total = flows.sum()
    if total < 1e-20:
        return 35.0  # safe fallback
    cp = 0.0
    for i, sp in enumerate(SPECIES):
        cp += (flows[i] / total) * _cp_shomate(sp, T)
    return cp


# ---------------------------------------------------------------------------
# VBF (1996) kinetics
# ---------------------------------------------------------------------------
def _vbf_rates(p: Dict[str, float], T: float) -> tuple[float, float]:
    """Vanden Bussche & Froment (1996) LHHW rate expressions.

    Parameters
    ----------
    p : dict
        Partial pressures of each species [bar].
    T : float
        Temperature [K].

    Returns
    -------
    r_meoh : float
        Rate of methanol synthesis (R1) [mol kgcat-1 s-1].
    r_rwgs : float
        Rate of reverse water-gas shift (R2) [mol kgcat-1 s-1].

    References
    ----------
    Vanden Bussche, K.M. & Froment, G.F.  J. Catal. 161 (1996) 1-10.
    Parameter values from Table 1 of the paper.
    """
    RT = R_GAS * T

    # Temperature-dependent kinetic and adsorption constants
    # Form: k_i = A_i * exp(B_i / (R*T))  -- note sign convention from VBF
    k1            = 1.22e10  * np.exp(-94765.0 / RT)
    k5a           = 1.09e5   * np.exp(-87500.0 / RT)
    KH2O_KH2half  = 6.62e-11 * np.exp(124119.0 / RT)
    KH2half       = 0.499    * np.exp( 17197.0 / RT)
    KH2O          = 6.37e-9  * np.exp(113700.0 / RT)

    # Lumped constant (dimensionless)
    KH2O_Keq1 = 3453.38

    # Thermodynamic equilibrium constants
    # Keq1: CO2 + 3H2 <=> CH3OH + H2O   [bar^-2]
    Keq1 = 10.0 ** (3066.0 / T - 10.592)
    # Keq3: CO2 + H2  <=> CO + H2O      [dimensionless]
    Keq3 = 10.0 ** (-2073.0 / T + 2.029)

    # Clamp partial pressures to small positive values
    pCO2  = max(p["CO2"],  1e-10)
    pH2   = max(p["H2"],   1e-10)
    pCO   = max(p["CO"],   1e-10)
    pMeOH = max(p["MeOH"], 1e-10)
    pH2O  = max(p["H2O"],  1e-10)

    # Denominator (adsorption term)
    denom = (1.0
             + KH2O_KH2half * (pH2O / max(pH2**0.5, 1e-10))
             + KH2half * pH2**0.5
             + KH2O * pH2O)

    # Guard against zero denominator
    denom = max(denom, 1e-10)

    # Driving forces
    # R1: methanol synthesis
    # VBF 1996 numerator: k5a * K' * pCO2 * pH2 * (1 - pMeOH*pH2O / (Keq1 * pCO2 * pH2^3))
    approach_meoh = 1.0 - (pMeOH * pH2O) / (max(Keq1, 1e-30) * pCO2 * pH2**3)
    driving_meoh = pCO2 * pH2 * approach_meoh
    r_meoh = k5a * KH2O_Keq1 * driving_meoh / denom**3


    # R2: reverse water-gas shift
    driving_rwgs = pCO2 * pH2 - pH2O * pCO / max(Keq3, 1e-30)
    r_rwgs = k1 * driving_rwgs / denom

    return float(r_meoh), float(r_rwgs)


# ---------------------------------------------------------------------------
# Configuration and result dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ReactorConfig:
    """Configuration for a single-tube packed-bed or membrane reactor."""

    # Geometry
    length_m: float = 1.0
    tube_diameter_m: float = 0.020
    catalyst_bulk_density_kg_m3: float = 1100.0
    void_fraction: float = 0.40
    particle_diameter_m: float = 1.5e-3

    # Operating conditions
    inlet_temperature_k: float = 493.15       # ~220 C
    inlet_pressure_bar: float = 30.0
    inlet_flow_mol_s: float = 2.0e-2
    h2_co2_ratio: float = 3.2
    co_feed_fraction: float = 0.0             # mol fraction of CO in reactive feed
    n2_feed_fraction: float = 0.0             # mol fraction N2 in total feed

    # Membrane
    membrane_enabled: bool = False
    water_permeance_mol_m2_s_pa: float = 1.0e-7
    sweep_water_partial_pressure_bar: float = 1.0e-4
    membrane_h2o_h2_selectivity: float = 200.0
    membrane_h2o_meoh_selectivity: float = 100.0

    # Thermal
    isothermal: bool = True
    coolant_temperature_k: float = 493.15
    overall_u_w_m2_k: float = 250.0


@dataclass
class ReactorResult:
    """Axial profiles and performance metrics from a reactor simulation."""

    z_m: np.ndarray                        # axial positions [m]
    flows_mol_s: Dict[str, np.ndarray]     # molar flow profiles
    temperature_k: np.ndarray              # temperature profile [K]
    pressure_bar: np.ndarray               # pressure profile [bar]
    metrics: Dict[str, float]              # scalar KPIs


# ---------------------------------------------------------------------------
# Feed calculator
# ---------------------------------------------------------------------------
def _feed(config: ReactorConfig) -> np.ndarray:
    """Compute inlet molar flow vector [mol s-1] for each species."""
    reactive = 1.0 - config.n2_feed_fraction
    co = reactive * config.co_feed_fraction
    co2 = (reactive - co) / (1.0 + config.h2_co2_ratio)
    h2 = config.h2_co2_ratio * co2
    n2 = config.n2_feed_fraction
    return config.inlet_flow_mol_s * np.array(
        [co2, h2, co, 0.0, 0.0, n2], dtype=float
    )


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------
def simulate_reactor(config: ReactorConfig) -> ReactorResult:
    """Integrate the 1-D reactor model along the tube axis.

    State vector (10 elements):
      y[0:6] = molar flows [mol s-1] for CO2, H2, CO, MeOH, H2O, N2
      y[6]   = temperature [K]
      y[7]   = pressure [Pa]
      y[8]   = cumulative water permeated through membrane [mol s-1]
      y[9]   = cumulative H2 permeated through membrane [mol s-1]

    Returns
    -------
    ReactorResult with axial profiles and performance metrics.
    """
    A_cs = np.pi * config.tube_diameter_m**2 / 4.0       # tube cross-section [m2]
    perim = np.pi * config.tube_diameter_m                # tube perimeter [m]
    inlet = _feed(config)
    P0_pa = config.inlet_pressure_bar * 1e5

    # Initial state
    y0 = np.zeros(10)
    y0[:6] = inlet
    y0[6] = config.inlet_temperature_k
    y0[7] = P0_pa
    y0[8] = 0.0   # cumulative H2O permeated
    y0[9] = 0.0   # cumulative H2 permeated

    def rhs(z: float, y: np.ndarray) -> np.ndarray:
        dy = np.zeros(10)

        # Unpack and clamp molar flows
        f = np.maximum(y[:6], 1e-18)
        T = max(y[6], 350.0)
        P_pa = max(y[7], 1e3)

        total = f.sum()
        P_bar = P_pa / 1e5

        # Partial pressures [bar]
        p_bar = {sp: (f[i] / total) * P_bar for i, sp in enumerate(SPECIES)}

        # --- Reaction rates [mol kgcat-1 s-1] ---
        r_meoh, r_rwgs = _vbf_rates(p_bar, T)

        # Source terms from reactions [mol s-1 per m of tube]
        # source_i = rho_cat * A_cs * sum_j(nu_ij * r_j)
        rates = np.array([r_meoh, r_rwgs])
        source = config.catalyst_bulk_density_kg_m3 * A_cs * (STOICH.T @ rates)

        # --- Membrane flux [mol m-2 s-1] ---
        flux = np.zeros(6)   # flux per unit membrane area
        if config.membrane_enabled:
            dp_h2o = max(p_bar["H2O"] - config.sweep_water_partial_pressure_bar, 0.0) * 1e5
            flux[4] = config.water_permeance_mol_m2_s_pa * dp_h2o     # H2O

            # Finite selectivity: H2 and MeOH crossover
            flux[1] = (config.water_permeance_mol_m2_s_pa
                       / config.membrane_h2o_h2_selectivity
                       * p_bar["H2"] * 1e5)                            # H2
            flux[3] = (config.water_permeance_mol_m2_s_pa
                       / config.membrane_h2o_meoh_selectivity
                       * p_bar["MeOH"] * 1e5)                          # MeOH

        # Species balances: dF_i/dz = source_i - perimeter * flux_i
        dy[:6] = source - perim * flux

        # --- Energy balance ---
        if config.isothermal:
            dy[6] = 0.0
        else:
            Cp_m = _cp_mix(f, T)
            # Heat generated by reactions [W m-1]
            q_rxn = config.catalyst_bulk_density_kg_m3 * A_cs * float(
                (-DH_RXN) @ rates
            )
            # Heat removed by coolant [W m-1]
            q_cool = config.overall_u_w_m2_k * perim * (T - config.coolant_temperature_k)
            dy[6] = (q_rxn - q_cool) / max(total * Cp_m, 1e-9)

        # --- Pressure drop (Ergun equation) ---
        # Superficial velocity
        vol_flow = total * R_GAS * T / P_pa              # m3 s-1 (ideal gas)
        u_s = vol_flow / A_cs                             # m s-1
        mu = 2.0e-5                                       # Pa s (assumed constant)

        # Gas density [kg m-3]
        mw_avg = sum(f[i] * MW[sp] for i, sp in enumerate(SPECIES)) / total
        rho_g = P_pa * mw_avg / (R_GAS * T)

        eps = config.void_fraction
        dp = config.particle_diameter_m
        dP_dz = -(150.0 * mu * (1 - eps)**2 / (dp**2 * eps**3) * u_s
                  + 1.75 * rho_g * (1 - eps) / (dp * eps**3) * u_s**2)
        dy[7] = dP_dz

        # --- Cumulative permeation tracking ---
        dy[8] = perim * flux[4]   # H2O permeated
        dy[9] = perim * flux[1]   # H2 permeated

        return dy

    # Solve
    sol = solve_ivp(
        rhs,
        (0.0, config.length_m),
        y0,
        method="BDF",
        rtol=1e-6,
        atol=1e-10,
        dense_output=False,
    )
    if not sol.success:
        raise RuntimeError(f"Reactor solver failed: {sol.message}")

    # Extract profiles
    flows = {sp: sol.y[i] for i, sp in enumerate(SPECIES)}
    T_profile = sol.y[6]
    P_profile = sol.y[7] / 1e5   # convert Pa -> bar

    # Compute metrics
    co2_in = inlet[0]
    co2_out = flows["CO2"][-1]
    meoh_out = flows["MeOH"][-1]
    h2_in = inlet[1]
    converted_co2 = max(co2_in - co2_out, 1e-18)
    cat_volume = A_cs * config.length_m * (1.0 - config.void_fraction)

    cum_h2o_perm = sol.y[8, -1]
    cum_h2_perm = sol.y[9, -1]
    h2o_outlet = flows["H2O"][-1]

    metrics = {
        "co2_conversion": float((co2_in - co2_out) / co2_in),
        "methanol_selectivity_carbon": float(meoh_out / converted_co2),
        "methanol_sty_kg_m3cat_h": float(
            meoh_out * MW["MeOH"] * 3600.0 / cat_volume
        ),
        "outlet_temperature_k": float(T_profile[-1]),
        "peak_temperature_k": float(T_profile.max()),
        "outlet_pressure_bar": float(P_profile[-1]),
        "pressure_drop_bar": float(config.inlet_pressure_bar - P_profile[-1]),
        "water_removed_fraction": float(
            cum_h2o_perm / max(cum_h2o_perm + h2o_outlet, 1e-18)
        ),
        "h2_loss_fraction": float(cum_h2_perm / max(h2_in, 1e-18)),
    }

    return ReactorResult(
        z_m=sol.t,
        flows_mol_s=flows,
        temperature_k=T_profile,
        pressure_bar=P_profile,
        metrics=metrics,
    )
