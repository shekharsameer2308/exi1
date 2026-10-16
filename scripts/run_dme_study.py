"""
scripts/run_dme_study.py
========================
Executes the comprehensive direct CO2-to-DME membrane reactor study:
1. Validation of traditional reactor (100x bed) against Gibbs equilibrium.
2. Sweeps over tube diameter d (4-10 mm) and sleeve thickness t (0.5-3.0 mm)
   at constant catalyst mass (0.12 kg) across NaA, LTA, and CMSM membranes.
3. Comparative benchmarking across reactor architectures (centre tube, concentric,
   shell-packed, lumen-packed, and sleeve bundle).
4. Practicality check: t >= 5 * dp.
5. High-resolution scale drawings and trend plots saved to figures/.
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure import path
sys.path.append(os.path.abspath('.'))
from dme_membrane_reactor import (
    run_dme_simulation,
    solve_gibbs_equilibrium,
    MEMBRANE_PROPERTIES,
)
from dme_bundle_reactor import bundle_layout

os.makedirs('figures', exist_ok=True)
os.makedirs('results', exist_ok=True)


def main():
    print("==================================================================")
    print("STEP 1: THERMODYNAMIC GIBBS EQUILIBRIUM & 100x BED VALIDATION")
    print("==================================================================")
    eq_res = solve_gibbs_equilibrium(T_K=523.15, P_bar=40.0, H2_CO2_ratio=3.0)
    print(f"Gibbs Equilibrium @ 250 C, 40 bar, H2/CO2=3:")
    print(f"  CO2 Conversion (X_eq):  {eq_res['X_CO2_eq']:.2f}%")
    print(f"  DME Yield (Y_eq):       {eq_res['Y_DME_eq']:.2f}%")
    print(f"  DME Selectivity (S_eq): {eq_res['S_DME_eq']:.2f}%")

    # Run 100x longer traditional reactor
    layout_base = bundle_layout(catalyst="sleeve", d=0.006, Ac=1.0e-4)
    tr_100x = run_dme_simulation(
        layout_base,
        membrane_type="NaA",
        is_membrane=False,
        T_C=250.0,
        P_ret_bar=40.0,
        L_m=100.0,
        GHSV_h=1000.0,
    )
    diff_X = abs(tr_100x['X_CO2'] - eq_res['X_CO2_eq'])
    diff_Y = abs(tr_100x['Y_DME'] - eq_res['Y_DME_eq'])
    print(f"\n100x Longer Traditional Reactor Output (L = 100 m):")
    print(f"  CO2 Conversion: {tr_100x['X_CO2']:.2f}% (Delta = {diff_X:.2f}%)")
    print(f"  DME Yield:      {tr_100x['Y_DME']:.2f}% (Delta = {diff_Y:.2f}%)")
    print(f"  Carbon Balance Error: {tr_100x['carbon_balance_error']:.2e}")
    assert tr_100x['carbon_balance_error'] < 1e-3, "Carbon balance error exceeded 1e-3!"
    assert diff_X < 0.2, "Traditional reactor did not reach Gibbs equilibrium within 0.2%!"
    print(">> VALIDATION PASSED: 100x bed accurately reaches Gibbs equilibrium!")

    print("\n==================================================================")
    print("STEP 2: WORKED CHECK & SLEEVE GEOMETRY VERIFICATION")
    print("==================================================================")
    check_geo = bundle_layout(catalyst="sleeve", d=0.006, Ac=1.0e-4)
    print(f"Worked check (d = 6.0 mm, Ac = 1e-4 m^2):")
    print(f"  Sleeve thickness t:       {check_geo['t']*1e3:.2f} mm (Expected: 1.12 mm)")
    print(f"  Shell diameter D:         {check_geo['D_shell']*1e3:.2f} mm (Expected: 19.9 mm)")
    print(f"  Area per bed volume av:   {check_geo['a_v']:.1f} m^-1 (Expected: ~755 m^-1)")
    print(f"  Shell void fraction:      {check_geo['void_fraction_shell']*100:.2f}%")
    print(f"  Center pocket void area:  {check_geo['A_center_void']*1e6:.2f} mm^2")
    print(f"  Four outer pockets area:  {check_geo['A_outer_voids']*1e6:.2f} mm^2")

    print("\n==================================================================")
    print("STEP 3: PARAMETRIC SWEEPS (d: 4-10 mm, t: 0.5-3.0 mm) AT CONSTANT MASS")
    print("==================================================================")
    # Sweeps across membranes: NaA, LTA, CMSM
    # Constant catalyst mass = 0.12 kg (rho_B = 1200 kg/m3 => V_bed = 1e-4 m3)
    V_bed_const = 1.0e-4
    rho_B = 1200.0
    W_cat_const = rho_B * V_bed_const  # 0.12 kg

    # Table 1: Sweep of tube diameter d (4, 6, 8, 10 mm) at nominal Ac = 1e-4 m2 (L = 1.0 m)
    d_list = [0.004, 0.006, 0.008, 0.010]
    sweep_d_results = []

    for d_val in d_list:
        layout = bundle_layout(catalyst="sleeve", d=d_val, Ac=1.0e-4, L=1.0)
        row = {
            "d_mm": d_val * 1e3,
            "t_mm": layout['t'] * 1e3,
            "d_s_mm": layout['d_s'] * 1e3,
            "D_shell_mm": layout['D_shell'] * 1e3,
            "a_v_m_inv": layout['a_v'],
            "is_practical": layout['is_practical'],
            "warning": layout['warning'],
            "membranes": {}
        }
        for mem in ["NaA", "LTA", "CMSM"]:
            sim = run_dme_simulation(layout, membrane_type=mem, is_membrane=True)
            row["membranes"][mem] = {
                "X_CO2": sim['X_CO2'],
                "Y_DME": sim['Y_DME'],
                "S_DME": sim['S_DME'],
                "water_removed_pct": sim['water_removed_pct'],
                "c_err": sim['carbon_balance_error']
            }
        sweep_d_results.append(row)

    # Table 2: Sweep of sleeve thickness t (0.5, 1.0, 1.5, 2.0, 2.5, 3.0 mm)
    # At fixed d = 6.0 mm, keeping catalyst mass constant at 0.12 kg by adjusting L = V_bed / Ac
    t_list = [0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030]
    sweep_t_results = []

    for t_val in t_list:
        # Ac = 4 * pi * t * (d + t)
        Ac_val = 4.0 * np.pi * t_val * (0.006 + t_val)
        L_val = V_bed_const / Ac_val  # Keep W_cat = 0.12 kg strictly constant
        layout = bundle_layout(catalyst="sleeve", d=0.006, t=t_val, L=L_val)

        row = {
            "t_mm": t_val * 1e3,
            "d_mm": 6.0,
            "L_m": L_val,
            "Ac_cm2": Ac_val * 1e4,
            "W_cat_kg": layout['W_cat'],
            "a_v_m_inv": layout['a_v'],
            "ratio_t_dp": layout['ratio_t_dp'],
            "is_practical": layout['is_practical'],
            "warning": layout['warning'],
            "membranes": {}
        }
        for mem in ["NaA", "LTA", "CMSM"]:
            sim = run_dme_simulation(layout, membrane_type=mem, is_membrane=True, L_m=L_val)
            row["membranes"][mem] = {
                "X_CO2": sim['X_CO2'],
                "Y_DME": sim['Y_DME'],
                "S_DME": sim['S_DME'],
                "water_removed_pct": sim['water_removed_pct'],
                "c_err": sim['carbon_balance_error']
            }
        sweep_t_results.append(row)

    print("\n==================================================================")
    print("STEP 4: ARCHITECTURAL COMPARISON (5 LAYOUTS AT CONSTANT 0.12 KG CATALYST)")
    print("==================================================================")
    # Benchmarking 5 layouts:
    # 1. Traditional Packed Bed (No membrane)
    # 2. One Centre Tube (Annulus catalyst)
    # 3. Four Concentric Membranes
    # 4. Four-Tube Bundle, Catalyst in Shell
    # 5. Four-Tube Bundle, Catalyst in Tubes
    # 6. Four-Tube Bundle, Uniform Sleeve (Proposed)

    bench_layouts = {
        "Traditional Reactor (TR)": bundle_layout("sleeve", d=0.006, Ac=1.0e-4),
        "One Centre Tube": bundle_layout("centre_tube", d1_centre=0.010, Ac=1.0e-4),
        "Four Concentric": bundle_layout("concentric", Ac=1.0e-4),
        "Four-Tube (Cat in Shell)": bundle_layout("shell", d=0.006, Ac=1.0e-4),
        "Four-Tube (Cat in Tubes)": bundle_layout("tubes", Ac=1.0e-4),
        "Four-Tube Sleeve Bundle": bundle_layout("sleeve", d=0.006, Ac=1.0e-4),
    }

    bench_results = {}
    for name, lay in bench_layouts.items():
        is_mem = (name != "Traditional Reactor (TR)")
        sim = run_dme_simulation(lay, membrane_type="NaA", is_membrane=is_mem)
        bench_results[name] = {
            "a_v": lay['a_v'] if is_mem else 0.0,
            "D_shell_mm": lay['D_shell'] * 1e3,
            "X_CO2": sim['X_CO2'],
            "Y_DME": sim['Y_DME'],
            "S_DME": sim['S_DME'],
            "water_removed_pct": sim['water_removed_pct'],
            "c_err": sim['carbon_balance_error'],
        }
        print(f"Layout: {name:28s} | a_v: {lay['a_v']:5.0f} m^-1 | X_CO2: {sim['X_CO2']:5.2f}% | Y_DME: {sim['Y_DME']:5.2f}% | H2O Rem: {sim['water_removed_pct']:5.2f}%")

    print("\n==================================================================")
    print("STEP 5: BYPASS ANALYSIS (SEALED VOIDS VS. UNSEALED BYPASS)")
    print("==================================================================")
    # If the voids are left unsealed, what is the hydraulic bypass fraction?
    # Hydraulic permeability: catalyst packed bed (Ergun Darcy permeability) vs open void channels (Poiseuille)
    # Pressure drop across open void is negligible, so feed severely channels through voids unless sealed!
    bypass_fractions = [0.0, 0.05, 0.10, 0.20, 0.314]  # 31.4% is area-weighted bypass
    bypass_results = []
    lay_sleeve = bundle_layout("sleeve", d=0.006, Ac=1.0e-4)

    for bf in bypass_fractions:
        sim = run_dme_simulation(lay_sleeve, membrane_type="NaA", is_membrane=True, bypass_fraction=bf)
        bypass_results.append({
            "bypass_fraction": bf,
            "X_CO2": sim['X_CO2'],
            "Y_DME": sim['Y_DME'],
            "S_DME": sim['S_DME'],
            "water_removed_pct": sim['water_removed_pct']
        })
        print(f"Bypass: {bf*100:4.1f}% | X_CO2: {sim['X_CO2']:5.2f}% | Y_DME: {sim['Y_DME']:5.2f}% | H2O Rem: {sim['water_removed_pct']:5.2f}%")

    # Save all data to results/dme_study_data.json
    all_data = {
        "worked_check": check_geo,
        "gibbs_validation": {
            "equilibrium": eq_res,
            "tr_100x": {
                "X_CO2": tr_100x['X_CO2'],
                "Y_DME": tr_100x['Y_DME'],
                "S_DME": tr_100x['S_DME'],
                "carbon_balance_error": tr_100x['carbon_balance_error']
            }
        },
        "sweep_d": sweep_d_results,
        "sweep_t": sweep_t_results,
        "bench_results": bench_results,
        "bypass_results": bypass_results,
    }
    with open('results/dme_study_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)

    print("\n==================================================================")
    print("STEP 6: GENERATING SCALE DRAWINGS & PUBLICATION-QUALITY PLOTS")
    print("==================================================================")
    plot_cross_section_to_scale(check_geo)
    plot_yield_trends(sweep_t_results, sweep_d_results)
    plot_layout_comparison(bench_results)

    print("\nAll steps completed successfully. Figures generated in figures/")


def plot_cross_section_to_scale(geo):
    """
    Draw the 4-tube catalyst sleeve reactor cross section strictly to scale.
    Features:
      - Cylindrical outer shell (diameter D)
      - 4 catalyst sleeves (outer diameter d_s, thickness t) touching each other and shell
      - 4 inner membrane tubes (diameter d) with central lumens
      - Central void pocket and 4 outer pockets clearly labeled as sealed voids / inert filler
    """
    d_mm = geo['d'] * 1e3
    t_mm = geo['t'] * 1e3
    ds_mm = geo['d_s'] * 1e3
    D_mm = geo['D_shell'] * 1e3

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

    # Shell outer wall
    R_shell = D_mm / 2.0
    shell_circle = plt.Circle((0, 0), R_shell, edgecolor='#1e293b', facecolor='#f1f5f9', linewidth=3, label='Shell Wall')
    ax.add_patch(shell_circle)

    # Center positions of the 4 touching sleeves
    # Form a square with side length = ds_mm, centered at origin
    # Distance from origin = ds_mm / sqrt(2)
    offset = ds_mm / 2.0
    centers = [
        (offset, offset),
        (-offset, offset),
        (-offset, -offset),
        (offset, -offset)
    ]

    # Draw Central Void Pocket (Hatched Inert/Sealed)
    # Highlighted background region
    center_void = plt.Polygon(
        [(0, 0), (offset, 0), (offset, offset), (0, offset)],
        closed=True, facecolor='none'
    )

    # Draw 4 Catalyst Sleeves
    rs_mm = ds_mm / 2.0
    rm_mm = d_mm / 2.0

    for i, (cx, cy) in enumerate(centers):
        # Catalyst sleeve outer boundary
        sleeve_patch = plt.Circle(
            (cx, cy), rs_mm,
            edgecolor='#0f766e', facecolor='#a7f3d0', linewidth=2,
            label='Catalyst Sleeve' if i == 0 else ""
        )
        ax.add_patch(sleeve_patch)

        # Membrane tube
        mem_patch = plt.Circle(
            (cx, cy), rm_mm,
            edgecolor='#1d4ed8', facecolor='#bfdbfe', linewidth=2,
            label='Membrane Tube (Permeate Lumen)' if i == 0 else ""
        )
        ax.add_patch(mem_patch)

    # Hatch the voids (sealed / inert pockets)
    # Central pocket
    c_void_patch = plt.Circle(
        (0, 0), (ds_mm / np.sqrt(2) - rs_mm) * 1.5,
        facecolor='none', edgecolor='#94a3b8', hatch='///'
    )

    # Annotations & Dimension Arrows
    # Diameter D
    ax.annotate(
        '', xy=(-R_shell, 0), xytext=(R_shell, 0),
        arrowprops=dict(arrowstyle='<->', color='#334155', lw=1.5)
    )
    ax.text(0, 0.8, f"Shell D = {D_mm:.1f} mm", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1e293b', backgroundcolor='#ffffff')

    # Membrane diameter d & sleeve thickness t
    cx0, cy0 = centers[0]
    ax.plot([cx0, cx0 + rs_mm], [cy0, cy0], color='#047857', lw=2)
    ax.text(cx0 + rs_mm/2, cy0 + 0.3, f"t={t_mm:.2f}mm", ha='center', va='bottom', fontsize=8, color='#065f46')

    # Void Labels
    ax.text(0, -rs_mm * 0.7, "Central Pocket\n(Sealed Void)", ha='center', va='center', fontsize=8, color='#64748b', style='italic')
    ax.text(0, R_shell * 0.82, "Peripheral Pocket (Sealed)", ha='center', va='center', fontsize=8, color='#64748b', style='italic')

    # Labels and Formatting
    ax.set_xlim(-R_shell * 1.15, R_shell * 1.15)
    ax.set_ylim(-R_shell * 1.15, R_shell * 1.15)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title(f"To-Scale Cross-Section: 4-Tube Sleeve Bundle CMR\n(d = {d_mm:.1f} mm, t = {t_mm:.2f} mm, d_s = {ds_mm:.2f} mm, D = {D_mm:.1f} mm)", fontsize=11, fontweight='bold', pad=15)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig('figures/dme_bundle_sleeve_cross_section.png', dpi=300)
    plt.close()
    print(">> Generated: figures/dme_bundle_sleeve_cross_section.png")


def plot_yield_trends(sweep_t, sweep_d):
    """
    Plot DME Yield, CO2 Conversion, and Water Removal against sleeve thickness t and tube diameter d.
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # 1. DME Yield vs Sleeve Thickness t
    ax1 = axes[0]
    t_vals = [r['t_mm'] for r in sweep_t]

    for mem, col, mark in [("NaA", "#059669", "o"), ("LTA", "#0284c7", "s"), ("CMSM", "#d97706", "^")]:
        y_vals = [r['membranes'][mem]['Y_DME'] for r in sweep_t]
        ax1.plot(t_vals, y_vals, marker=mark, lw=2.2, color=col, label=f"{mem} Membrane")

    # Add Traditional Reactor baseline
    ax1.axhline(31.15, color='#dc2626', linestyle='--', lw=1.8, label="Traditional Packed Bed (TR: 31.2%)")
    ax1.axhline(46.54, color='#7c3aed', linestyle=':', lw=1.8, label="Gibbs Equilibrium Ceiling (46.5%)")

    # Shaded impractical region (t < 5 * dp, dp=0.3mm => t < 1.5mm)
    ax1.axvspan(0.4, 1.5, color='#fee2e2', alpha=0.5, label='Impractical Region (t < 5*dp)')

    ax1.set_xlabel("Sleeve Thickness, t [mm]", fontsize=10, fontweight='bold')
    ax1.set_ylabel("DME Single-Pass Yield [%]", fontsize=10, fontweight='bold')
    ax1.set_title("DME Yield vs. Sleeve Thickness t (d = 6 mm, Wcat = 0.12 kg)", fontsize=10, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(fontsize=8, loc='best')

    # 2. Key Metrics vs Tube Diameter d
    ax2 = axes[1]
    d_vals = [r['d_mm'] for r in sweep_d]

    # Plot NaA results across d
    y_dme = [r['membranes']['NaA']['Y_DME'] for r in sweep_d]
    x_co2 = [r['membranes']['NaA']['X_CO2'] for r in sweep_d]
    w_rem = [r['membranes']['NaA']['water_removed_pct'] for r in sweep_d]

    ax2.plot(d_vals, y_dme, marker='o', lw=2.2, color='#059669', label='DME Yield [%]')
    ax2.plot(d_vals, x_co2, marker='s', lw=2.2, color='#1e293b', label='CO2 Conversion [%]')
    ax2.plot(d_vals, w_rem, marker='^', lw=2.2, color='#0284c7', label='Water Removed [%]')

    ax2.set_xlabel("Membrane Tube Diameter, d [mm]", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Process Performance [%]", fontsize=10, fontweight='bold')
    ax2.set_title("Performance vs. Tube Diameter d (NaA Zeolite, Ac = 1e-4 m^2)", fontsize=10, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(fontsize=8, loc='best')

    plt.tight_layout()
    plt.savefig('figures/dme_yield_vs_thickness.png', dpi=300)
    plt.close()
    print(">> Generated: figures/dme_yield_vs_thickness.png")


def plot_layout_comparison(bench_results):
    """
    Bar chart comparison across 5 configurations at identical catalyst mass (0.12 kg).
    """
    layouts = list(bench_results.keys())
    x_conv = [bench_results[k]['X_CO2'] for k in layouts]
    y_dme = [bench_results[k]['Y_DME'] for k in layouts]
    h2o_rem = [bench_results[k]['water_removed_pct'] for k in layouts]

    x = np.arange(len(layouts))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
    rects1 = ax.bar(x - width, x_conv, width, label='CO2 Conversion [%]', color='#334155')
    rects2 = ax.bar(x, y_dme, width, label='DME Yield [%]', color='#059669')
    rects3 = ax.bar(x + width, h2o_rem, width, label='Water Removed [%]', color='#0284c7')

    # Add Gibbs equilibrium line
    ax.axhline(48.71, color='#7c3aed', linestyle=':', lw=1.5, label='Gibbs CO2 Conv Ceiling (48.7%)')

    ax.set_ylabel('Performance Metric [%]', fontsize=10, fontweight='bold')
    ax.set_title('Direct CO2-to-DME Architectural Comparison (Identical Catalyst Mass = 0.12 kg)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(layouts, rotation=15, ha='right', fontsize=9)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, axis='y', linestyle=':', alpha=0.6)

    # Bar value labels
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=7, fontweight='bold')

    plt.tight_layout()
    plt.savefig('figures/dme_layout_comparison.png', dpi=300)
    plt.close()
    print(">> Generated: figures/dme_layout_comparison.png")


if __name__ == '__main__':
    main()
