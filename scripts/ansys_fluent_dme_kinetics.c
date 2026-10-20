/*
 * ansys_fluent_dme_kinetics.c
 * ============================
 * ANSYS Fluent User-Defined Functions (UDF) for direct CO2-to-DME
 * catalytic membrane reactor models (Single-Tube and Four-Tube Shell-Packed).
 *
 * 1. Reaction Kinetics:
 *    - Reactions 1 & 2: Mignard & Pritchard (2008) / Vanden Bussche & Froment (1996)
 *      over commercial Cu/ZnO/Al2O3.
 *    - Reaction 3: Solid acid methanol dehydration over H-ZSM-5
 *      r3 = k3 * (p_MeOH^2 / p_H2O - p_DME / Kp3) (Lu et al. 2004 / Poto et al. 2021)
 *    - Thermodynamics: Graaf et al. (1986) & Lu et al. (2004) / Poto et al. (2021).
 *
 * 2. Selective Membrane Water Extraction:
 *    - NaA Zeolite: Permeance = 1.8e-7 mol/(m2*s*Pa), Selectivity > 10,000 vs DME.
 *
 * Applicable to:
 *    - Model 1: Single Centre Tube CMR (2D Axisymmetric or 3D)
 *    - Model 2: Four-Tube Shell-Packed CMR (Case Study B, 3D / Quarter-Symmetry)
 */

#include "udf.h"
#include <math.h>

#define RGAS 8.314462618   /* J / (mol * K) */
#define RHO_BULK 1200.0    /* Catalyst bulk density: kg / m^3 */

/*
 * DEFINE_VR_RATE: Volumetric reaction rates in the porous catalyst bed.
 * Evaluates r1 (MeOH), r2 (RWGS), and r3 (DME dehydration).
 * Output *rate is in kmol / (m^3 * s).
 */
DEFINE_VR_RATE(user_dme_kinetics, c, t, r, mole_frac, yi, rate, rr_t)
{
    real T = C_T(c, t);                    /* Temperature in Kelvin */
    real P_gauge = C_P(c, t);              /* Gauge pressure in Pa */
    real P_tot_bar = (P_gauge + 101325.0) / 1.0e5; /* Absolute pressure in bar */

    /* Species order in mixture:
     * 0: CO2, 1: H2, 2: H2O, 3: CH3OH, 4: CO, 5: CH3OCH3 (DME)
     */
    real p_CO2  = fmax(1e-12, mole_frac[0] * P_tot_bar);
    real p_H2   = fmax(1e-12, mole_frac[1] * P_tot_bar);
    real p_H2O  = fmax(1e-12, mole_frac[2] * P_tot_bar);
    real p_MeOH = fmax(1e-12, mole_frac[3] * P_tot_bar);
    real p_CO   = fmax(1e-12, mole_frac[4] * P_tot_bar);
    real p_DME  = fmax(1e-12, mole_frac[5] * P_tot_bar);

    /* --- Thermodynamic Equilibrium Constants ---
     * Reactions 1 & 2: Graaf et al. (1986)
     * Reaction 3: Lu et al. (2004) / Poto et al. (2021)
     */
    real Keq1 = pow(10.0, (3066.0 / T - 10.592)); /* bar^-2 */
    real Keq2 = pow(10.0, (-2073.0 / T + 2.029)); /* dimensionless */
    real ln_Kp3 = (4019.0 / T) + (3.707 * log(T)) - (2.783e-3 * T) 
                  + (3.8e-7 * T * T) - (6.561e4 / (T * T * T)) - 26.64;
    real Kp3 = exp(ln_Kp3); /* dimensionless */

    /* --- Kinetic Rate Parameters: Mignard & Pritchard (2008) --- */
    real k1 = 1.07 * exp(40000.0 / (RGAS * T));
    real k2 = 1.22e10 * exp(-98084.0 / (RGAS * T));
    real K_H2O = 6.62e-11 * exp(124119.0 / (RGAS * T));
    real sqrt_K_H2 = 0.499 * exp(17197.0 / (RGAS * T));
    real K_H2O_H2 = 3453.38;

    /* Langmuir-Hinshelwood active-site denominator */
    real D_k = 1.0 + K_H2O_H2 * (p_H2O / p_H2) + sqrt_K_H2 * sqrt(p_H2) + K_H2O * p_H2O;
    real D_k3 = D_k * D_k * D_k;

    /* Driving force ratios */
    real term1 = (p_H2O * p_MeOH) / (Keq1 * pow(p_H2, 3.0) * p_CO2 + 1e-15);
    real term2 = (p_H2O * p_CO) / (Keq2 * p_H2 * p_CO2 + 1e-15);

    /* Rates in mol / (kg_cat * s) */
    real r1_mol = k1 * p_CO2 * p_H2 * (1.0 - term1) / D_k3;
    real r2_mol = k2 * p_CO2 * (1.0 - term2) / D_k;

    /* --- Reaction 3: Methanol Dehydration (Lu et al. 2004 / Poto et al. 2021) ---
     * r3 = k3 * (p_MeOH^2 / p_H2O - p_DME / Kp3)
     * k3 = 8.2894e4 * exp(-5.2940e4 / (R*T)) [kmol / (kg_cat * s * bar)]
     *    = 8.2894e7 * exp(-5.2940e4 / (R*T)) [mol / (kg_cat * s * bar)]
     */
    real k3_mol = 8.2894e7 * exp(-5.2940e4 / (RGAS * T)); /* mol / (kg_cat * s * bar) */
    real p_H2O_safe = fmax(p_H2O, 1.0e-6); /* Numerical safeguard near inlet */
    real r3_driving_force = (p_MeOH * p_MeOH) / p_H2O_safe - (p_DME / Kp3);
    real r3_mol = k3_mol * r3_driving_force;

    /* Convert mol/(kg_cat * s) -> kmol/(m^3 * s) for Fluent:
     * rate [kmol/(m^3*s)] = rate [mol/(kg*s)] * rho_bulk [kg/m^3] * 1e-3 [kmol/mol]
     */
    real conversion_factor = RHO_BULK * 1.0e-3; /* = 1.20 */

    if (r == 0)      *rate = fmax(0.0, r1_mol * conversion_factor);
    else if (r == 1) *rate = fmax(0.0, r2_mol * conversion_factor);
    else if (r == 2) *rate = fmax(0.0, r3_mol * conversion_factor);
}

/*
 * DEFINE_SOURCE: Selective Membrane Water Extraction
 * Calculates transmembrane water permeation into the NaA zeolite pores.
 * 
 * Permeance = 1.8e-7 mol / (m^2 * s * Pa)
 * Applicable as a volumetric mass sink near the membrane interface:
 * S_m = -J * a_v * MW_H2O [kg / (m^3 * s)]
 */
DEFINE_SOURCE(water_naa_membrane_sink, c, t, dS, eqn)
{
    real Perm_H2O = 1.8e-7; /* mol / (m^2 * s * Pa) */
    real P_tot_Pa = C_P(c, t) + 101325.0;

    /* Molecular weights [kg/kmol]:
     * 0: CO2 (44.01), 1: H2 (2.016), 2: H2O (18.015), 
     * 3: CH3OH (32.042), 4: CO (28.01), 5: DME (46.069)
     */
    real mw[6] = {44.01, 2.016, 18.015, 32.042, 28.01, 46.069};
    real sum_y_over_m = 0.0;
    int i;
    for (i = 0; i < 6; i++) {
        sum_y_over_m += C_YI(c, t, i) / mw[i];
    }
    
    /* Water mole fraction */
    real x_H2O = (C_YI(c, t, 2) / mw[2]) / fmax(sum_y_over_m, 1e-15);
    real p_H2O_ret = x_H2O * P_tot_Pa;

    /* Permeate sweep maintained at 1 bar (sweep partial pressure ~ 1000 Pa) */
    real p_H2O_perm = 1000.0;
    real delta_p = fmax(0.0, p_H2O_ret - p_H2O_perm);

    /* Specific membrane area:
     * - Single-Tube CMR: a_v = 133.33 m^-1
     * - Four-Tube Shell-Packed CMR: a_v = 266.67 m^-1
     */
    real av = 266.67; /* Default to Four-Tube model (set 133.33 for Single Tube) */
    real MW_H2O = 0.018015; /* kg / mol */

    real source = -1.0 * Perm_H2O * delta_p * av * MW_H2O;
    dS[eqn] = -1.0 * Perm_H2O * av * MW_H2O * (P_tot_Pa / mw[2]) / fmax(sum_y_over_m, 1e-15);

    return source;
}
