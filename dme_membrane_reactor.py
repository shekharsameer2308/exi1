"""
dme_membrane_reactor.py
=======================
1D Steady-State Plug-Flow Reactor Model for Direct CO2-to-DME Synthesis
with In-Situ Membrane Water Removal.

Reactions:
  (1) CO2 + 3 H2 <-> CH3OH + H2O      (Methanol Synthesis)
  (2) CO2 + H2   <-> CO + H2O          (Reverse Water-Gas Shift, RWGS)
  (3) 2 CH3OH    <-> CH3OCH3 + H2O     (Methanol Dehydration to DME)

References:
  - Kinetics (1 & 2): Vanden Bussche & Froment (1996), modified by Mignard & Pritchard (2008)
  - Kinetics (3): Reversible methanol dehydration over solid acid (placeholder rate constant)
  - Membrane Permeance & Selectivities: Table 2 of Richard et al., Int. J. Hydrogen Energy 112 (2025) 446-467
    * NaA Zeolite: Li et al. (2020), Dong et al. (2022)
    * LTA Zeolite: Ateka et al. (2021)
    * CMSM (Carbon Molecular Sieve): Poto et al. (2023)
  - Thermodynamic equilibrium: Stull (1969), Graaf et al. (1986), Ng et al. (1999)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

R_GAS = 8.314462618  # J / (mol * K)

# ---------------------------------------------------------------------------
# Membrane Library (Richard et al. 2025, Table 2)
# ---------------------------------------------------------------------------
# Permeance in mol / (m^2 * s * Pa)
# Selectivity alpha(H2O / i)
MEMBRANE_PROPERTIES = {
    "NaA": {
        "name": "NaA Zeolite (Li 2020, Dong 2022)",
        "permeance_H2O": 1.8e-7,  # mol / (m^2 * s * Pa)
        "selectivity": {
            "CO2": 5000.0,
            "H2": 1000.0,
            "H2O": 1.0,
            "CH3OH": 2000.0,
            "CO": 5000.0,
            "DME": 10000.0,  # DME kinetic diameter 4.3 A vs NaA pore 4.0 A (virtually impermeable)
        },
        "source": "Richard et al. 2025, Table 2 (Li 2020; Dong 2022)",
    },
    "LTA": {
        "name": "LTA Zeolite (Ateka 2021)",
        "permeance_H2O": 2.0e-7,  # mol / (m^2 * s * Pa)
        "selectivity": {
            "CO2": 3000.0,
            "H2": 800.0,
            "H2O": 1.0,
            "CH3OH": 1500.0,
            "CO": 3000.0,
            "DME": 10000.0,
        },
        "source": "Richard et al. 2025, Table 2 (Ateka 2021)",
    },
    "CMSM": {
        "name": "Carbon Molecular Sieve Membrane (Poto 2023)",
        "permeance_H2O": 0.6e-7,  # mol / (m^2 * s * Pa)
        "selectivity": {
            "CO2": 250.0,
            "H2": 80.0,
            "H2O": 1.0,
            "CH3OH": 500.0,
            "CO": 250.0,
            "DME": 2000.0,
        },
        "source": "Richard et al. 2025, Table 2 (Poto 2023)",
    },
}

SPECIES = ["CO2", "H2", "H2O", "CH3OH", "CO", "DME"]
N_SPECIES = len(SPECIES)


def calculate_equilibrium_constants(T_K):
    """
    Thermodynamic equilibrium constants for direct CO2-to-DME network:
      Keq1: CO2 + 3H2 <-> CH3OH + H2O      [bar^-2] (Graaf / Mignard & Pritchard)
      Keq2: CO2 + H2  <-> CO + H2O          [-]      (Graaf / Bisotti)
      Keq3: 2 CH3OH   <-> DME + H2O         [-]      (Stull / Ng et al. 1999)
    """
    Keq1 = 10.0 ** (3066.0 / T_K - 10.592)          # bar^-2
    Keq2 = 10.0 ** (-2073.0 / T_K + 2.029)          # dimensionless
    Keq3 = 10.0 ** (2226.0 / T_K - 0.910)           # dimensionless (Stull / Ng 1999)
    return Keq1, Keq2, Keq3


def calculate_dme_kinetics(T_K, p_bar, k_dme_placeholder=0.05):
    """
    Reaction rate evaluation [mol / (kg_cat * s)].

    Reactions:
      (1) CO2 + 3H2 <-> CH3OH + H2O
      (2) CO2 + H2   <-> CO + H2O
      (3) 2 CH3OH    <-> DME + H2O

    NOTE on Reaction 3:
      As required by project instructions, the dehydration rate constant
      `k_dme_placeholder` is a clearly labelled placeholder constant:
      k_DME = 0.05 mol / (kg_cat * s * bar^2) (bifunctional acid catalyst).
    """
    p_safe = np.maximum(p_bar, 1e-12)
    pCO2, pH2, pH2O, pMeOH, pCO, pDME = p_safe

    Keq1, Keq2, Keq3 = calculate_equilibrium_constants(T_K)

    # --- Kinetics 1 & 2: Mignard & Pritchard (2008) ---
    k1 = 1.07 * np.exp(40000.0 / (R_GAS * T_K))
    k2 = 1.22e10 * np.exp(-98084.0 / (R_GAS * T_K))
    K_H2O = 6.62e-11 * np.exp(124119.0 / (R_GAS * T_K))
    sqrt_K_H2 = 0.499 * np.exp(17197.0 / (R_GAS * T_K))
    K_H2O_H2 = 3453.38

    D_k = 1.0 + K_H2O_H2 * (pH2O / pH2) + sqrt_K_H2 * np.sqrt(pH2) + K_H2O * pH2O

    term1 = (pH2O * pMeOH) / (Keq1 * (pH2 ** 3) * pCO2)
    term2 = (pH2O * pCO) / (Keq2 * pH2 * pCO2)

    r1 = k1 * pCO2 * pH2 * (1.0 - term1) / (D_k ** 3)
    r2 = k2 * pCO2 * (1.0 - term2) / D_k

    # --- Kinetics 3: Methanol Dehydration (Clearly Labelled Placeholder) ---
    # r3 = k_DME * (p_MeOH^2 - (p_DME * p_H2O) / Keq3)
    term3 = (pDME * pH2O) / (Keq3 * (pMeOH ** 2))
    r3 = k_dme_placeholder * (pMeOH ** 2) * (1.0 - term3)

    return r1, r2, r3


def solve_gibbs_equilibrium(T_K=523.15, P_bar=40.0, H2_CO2_ratio=3.0):
    """
    Thermodynamic Gibbs equilibrium conversion and DME yield calculation.
    Used for 100x bed length validation benchmark.
    """
    Keq1, Keq2, Keq3 = calculate_equilibrium_constants(T_K)

    # Basis: 1 mol CO2, H2_CO2_ratio mol H2
    n_CO2_0 = 1.0
    n_H2_0 = float(H2_CO2_ratio)

    def objective(extents):
        xi1, xi2, xi3 = extents
        n_CO2 = n_CO2_0 - xi1 - xi2
        n_H2 = n_H2_0 - 3.0 * xi1 - xi2
        n_H2O = xi1 + xi2 + xi3
        n_MeOH = xi1 - 2.0 * xi3
        n_CO = xi2
        n_DME = xi3

        if min(n_CO2, n_H2, n_H2O, n_MeOH, n_CO, n_DME) <= 0.0:
            return 1e8

        n_tot = n_CO2 + n_H2 + n_H2O + n_MeOH + n_CO + n_DME
        p = np.array([n_CO2, n_H2, n_H2O, n_MeOH, n_CO, n_DME]) / n_tot * P_bar

        res1 = np.log((p[2] * p[3]) / ((p[1] ** 3) * p[0])) - np.log(Keq1)
        res2 = np.log((p[2] * p[4]) / (p[1] * p[0])) - np.log(Keq2)
        res3 = np.log((p[5] * p[2]) / (p[3] ** 2)) - np.log(Keq3)

        return res1 ** 2 + res2 ** 2 + res3 ** 2

    bounds = [(1e-5, 0.99), (1e-5, 0.99), (1e-5, 0.495)]
    constraints = [
        {"type": "ineq", "fun": lambda x: n_CO2_0 - x[0] - x[1]},
        {"type": "ineq", "fun": lambda x: x[0] - 2.0 * x[2]},
        {"type": "ineq", "fun": lambda x: n_H2_0 - 3.0 * x[0] - x[1]},
    ]

    res = minimize(objective, [0.45, 0.02, 0.22], bounds=bounds, constraints=constraints, method="SLSQP", tol=1e-12)
    xi1, xi2, xi3 = res.x

    X_CO2 = (xi1 + xi2) / n_CO2_0 * 100.0
    Y_DME = (2.0 * xi3) / n_CO2_0 * 100.0
    S_DME = (2.0 * xi3) / (xi1 + xi2) * 100.0

    return {
        "X_CO2_eq": float(X_CO2),
        "Y_DME_eq": float(Y_DME),
        "S_DME_eq": float(S_DME),
        "extents": (float(xi1), float(xi2), float(xi3)),
    }


def run_dme_simulation(
    layout_dict,
    membrane_type="NaA",
    is_membrane=True,
    T_C=250.0,
    P_ret_bar=40.0,
    P_perm_bar=1.0,
    H2_CO2_ratio=3.0,
    GHSV_h=1000.0,
    sweep_ratio=1.0,
    L_m=1.0,
    rho_B=1200.0,
    k_dme=0.05,
    bypass_fraction=0.0,
    F_feed_tot=None,
):
    """
    1D Plug-Flow Simulation of Catalytic Membrane Reactor for DME Synthesis.

    Parameters:
      layout_dict: dictionary from bundle_layout containing Ac, Pm, etc.
      membrane_type: "NaA", "LTA", or "CMSM"
      is_membrane: bool (True for MR, False for traditional reactor TR)
      T_C: temperature in Celsius (default 250 °C)
      P_ret_bar: retentate feed pressure (default 40 bar)
      P_perm_bar: permeate pressure (default 1 bar)
      H2_CO2_ratio: inlet syngas ratio (default 3.0)
      GHSV_h: Gas Hourly Space Velocity (default 1000 h^-1 STP, based on nominal 1m bed)
      sweep_ratio: sweep to feed ratio (default 1.0)
      L_m: reactor length (default 1.0 m)
      rho_B: catalyst bulk density (default 1200 kg/m^3)
      k_dme: placeholder DME dehydration rate constant
      bypass_fraction: fraction of feed bypassing catalyst (if unsealed voids)
      F_feed_tot: total molar feed rate [mol/s] (optional, overrides GHSV)

    Returns:
      dict with conversions, yields, selectivity, water removed, carbon balance error.
    """
    T_K = T_C + 273.15
    P_ret_Pa = P_ret_bar * 1e5
    P_perm_Pa = P_perm_bar * 1e5

    Ac = layout_dict["Ac"]
    Pm = layout_dict["Pm"] if is_membrane else 0.0

    # Total reaction volume and catalyst mass
    V_bed = Ac * L_m
    W_cat = rho_B * V_bed

    # Feed flow rate
    if F_feed_tot is None:
        # Base feed flow on nominal bed volume (Ac * 1.0 m) so lengthening bed increases residence time
        V_ref = Ac * 1.0
        Q_stp = V_ref * GHSV_h / 3600.0
        F_feed_tot = Q_stp / 0.022414  # mol / s

    # Feed composition (H2 / CO2 = H2_CO2_ratio)
    y_CO2_in = 1.0 / (1.0 + H2_CO2_ratio)
    y_H2_in = H2_CO2_ratio / (1.0 + H2_CO2_ratio)

    F_CO2_0 = F_feed_tot * y_CO2_in
    F_H2_0 = F_feed_tot * y_H2_in

    # Active flow entering catalyst vs bypass
    F_active_in = np.array([F_CO2_0, F_H2_0, 0.0, 0.0, 0.0, 0.0]) * (1.0 - bypass_fraction)
    F_bypass = np.array([F_CO2_0, F_H2_0, 0.0, 0.0, 0.0, 0.0]) * bypass_fraction

    # Sweep gas on permeate side
    F_sweep_in = sweep_ratio * F_feed_tot

    # Membrane properties
    mem_info = MEMBRANE_PROPERTIES.get(membrane_type, MEMBRANE_PROPERTIES["NaA"])
    Pi_H2O = mem_info["permeance_H2O"]
    selectivity = mem_info["selectivity"]
    Pi_vec = np.array([
        Pi_H2O / selectivity["CO2"],
        Pi_H2O / selectivity["H2"],
        Pi_H2O / selectivity["H2O"],
        Pi_H2O / selectivity["CH3OH"],
        Pi_H2O / selectivity["CO"],
        Pi_H2O / selectivity["DME"],
    ])

    def ode_system(z, y):
        # y[0:6] = retentate flows (CO2, H2, H2O, MeOH, CO, DME)
        # y[6:12] = permeate flows
        F_ret = np.maximum(y[0:6], 1e-13)
        F_perm = np.maximum(y[6:12], 1e-13)

        F_tot_ret = np.sum(F_ret)
        p_ret_Pa = (F_ret / F_tot_ret) * P_ret_Pa
        p_ret_bar = p_ret_Pa * 1e-5

        F_tot_perm = np.sum(F_perm) + F_sweep_in
        p_perm_Pa = (F_perm / F_tot_perm) * P_perm_Pa

        # Chemical Kinetics
        r1, r2, r3 = calculate_dme_kinetics(T_K, p_ret_bar, k_dme_placeholder=k_dme)

        # Net reaction rates [mol / (kg_cat * s)]
        # Species: CO2, H2, H2O, CH3OH, CO, DME
        r_net = np.zeros(6)
        r_net[0] = -r1 - r2
        r_net[1] = -3.0 * r1 - r2
        r_net[2] = r1 + r2 + r3
        r_net[3] = r1 - 2.0 * r3
        r_net[4] = r2
        r_net[5] = r3

        dF_ret = r_net * rho_B * Ac
        dF_perm = np.zeros(6)

        if is_membrane and Pm > 0.0:
            dp = np.maximum(p_ret_Pa - p_perm_Pa, 0.0)
            flux = Pi_vec * dp  # mol / (m^2 * s)

            # Numerical stability: cannot permeate more than currently available
            flux = np.minimum(flux, F_ret / (Pm * 1e-3))

            trans_rate = flux * Pm  # mol / (m * s)
            dF_ret -= trans_rate
            dF_perm = trans_rate

        return np.concatenate([dF_ret, dF_perm])

    y0 = np.concatenate([F_active_in, np.zeros(6)])
    sol = solve_ivp(
        ode_system,
        [0.0, L_m],
        y0,
        method="BDF",
        atol=1e-10,
        rtol=1e-8,
        t_eval=np.linspace(0.0, L_m, 60),
    )

    # Add back any bypass stream at reactor exit
    F_ret_final = sol.y[0:6, -1] + F_bypass
    F_perm_final = sol.y[6:12, -1]

    # Performance Metrics
    F_CO2_in = F_CO2_0
    X_CO2 = (F_CO2_in - F_ret_final[0]) / F_CO2_in * 100.0
    Y_DME = (2.0 * F_ret_final[5]) / F_CO2_in * 100.0
    S_DME = (2.0 * F_ret_final[5]) / (F_CO2_in - F_ret_final[0] + 1e-14) * 100.0

    total_water_generated = F_ret_final[2] + F_perm_final[2]
    water_removed_pct = (F_perm_final[2] / (total_water_generated + 1e-14)) * 100.0

    # Carbon Balance Error
    C_in = F_CO2_in
    C_out = (
        (F_ret_final[0] + F_ret_final[3] + F_ret_final[4] + 2.0 * F_ret_final[5])
        + (F_perm_final[0] + F_perm_final[3] + F_perm_final[4] + 2.0 * F_perm_final[5])
    )
    carbon_balance_error = abs(C_in - C_out) / C_in

    return {
        "success": sol.success,
        "membrane": membrane_type if is_membrane else "None (TR)",
        "X_CO2": float(X_CO2),
        "Y_DME": float(Y_DME),
        "S_DME": float(S_DME),
        "water_removed_pct": float(water_removed_pct),
        "carbon_balance_error": float(carbon_balance_error),
        "F_ret_out": F_ret_final.tolist(),
        "F_perm_out": F_perm_final.tolist(),
        "F_in": [F_CO2_0, F_H2_0],
        "W_cat_kg": float(W_cat),
        "L_m": float(L_m),
        "z": sol.t.tolist(),
        "profiles_ret": sol.y[0:6, :].tolist(),
        "profiles_perm": sol.y[6:12, :].tolist(),
    }
