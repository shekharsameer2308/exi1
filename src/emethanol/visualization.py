"""
Publication-quality visualization and pseudo-2D reactor contour generation module.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable

from src.emethanol.reactor import simulate_reactor, ReactorSimulationResult, ModelConfig

# Standardized color palette adhering to project rules
# Slate #475569, Emerald #10b981, Red #ef4444, Gray #6b7280, Cyan #06b6d4, Amber #f59e0b
COLORS = {
    "slate": "#475569",
    "emerald": "#10b981",
    "red": "#ef4444",
    "gray": "#6b7280",
    "cyan": "#06b6d4",
    "amber": "#f59e0b",
    "co2": "#475569",
    "h2": "#0ea5e9",
    "co": "#f59e0b",
    "meoh": "#10b981",
    "h2o": "#ef4444",
    "temp": "#e11d48",
    "pressure": "#6366f1",
}


def setup_matplotlib_style():
    """Sets publication-grade minimalist matplotlib parameters."""
    plt.rcParams.update({
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 13,
        "axes.edgecolor": "#cbd5e1",
        "axes.linewidth": 1.0,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
    })


def generate_reactor_contour(
    parameter_name: str,
    parameter_values: np.ndarray,
    target_variable: str = "CH3OH",
    fixed_conditions: Optional[Dict[str, Any]] = None,
    n_points_z: int = 50,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """
    Generates a 1D-derived pseudo-2D performance contour map along the reactor length.
    
    Parameters
    ----------
    parameter_name : str
        Swept parameter (e.g., 'temperature', 'pressure', 'h2_co2_ratio', 'water_permeance', 'total_flow')
    parameter_values : np.ndarray
        Array of parameter values (Y-axis)
    target_variable : str
        Target profile to contour (e.g., 'CH3OH', 'CO2', 'H2', 'H2O', 'CO', 'temperature', 'r_meoh', 'j_h2o')
    fixed_conditions : Dict[str, Any]
        Base simulation conditions
        
    Returns
    -------
    Tuple[Z_grid, Param_grid, Target_Matrix, title_str]
    """
    cond = {
        "temperature": 493.15,
        "pressure": 50.0,
        "total_flow": 0.015,
        "h2_co2_ratio": 3.0,
        "water_permeance": 1.0e-7,
        "reactor_length": 1.0,
        "reactor_diameter": 0.02,
        "membrane_enabled": True,
        "non_isothermal": True,
        "pressure_drop": False,
    }
    if fixed_conditions:
        cond.update(fixed_conditions)

    n_params = len(parameter_values)
    z_eval = np.linspace(0, cond["reactor_length"], n_points_z)
    target_matrix = np.zeros((n_params, n_points_z))

    for i, val in enumerate(parameter_values):
        run_cond = cond.copy()
        run_cond[parameter_name] = float(val)
        res = simulate_reactor(**run_cond)
        
        if res.solver_success:
            # Interpolate to common z_grid
            if target_variable.upper() in ["CH3OH", "MEOH", "Y_CH3OH"]:
                y_data = np.interp(z_eval, res.z_grid, res.y_CH3OH * 100.0) # %
            elif target_variable.upper() in ["CO2", "Y_CO2"]:
                y_data = np.interp(z_eval, res.z_grid, res.y_CO2 * 100.0)
            elif target_variable.upper() in ["H2", "Y_H2"]:
                y_data = np.interp(z_eval, res.z_grid, res.y_H2 * 100.0)
            elif target_variable.upper() in ["H2O", "Y_H2O"]:
                y_data = np.interp(z_eval, res.z_grid, res.y_H2O * 100.0)
            elif target_variable.upper() in ["CO", "Y_CO"]:
                y_data = np.interp(z_eval, res.z_grid, res.y_CO * 100.0)
            elif target_variable.upper() in ["TEMPERATURE", "T"]:
                y_data = np.interp(z_eval, res.z_grid, res.T_profile)
            elif target_variable.upper() in ["R_MEOH", "REACTION_RATE"]:
                y_data = np.interp(z_eval, res.z_grid, res.r_meoh_profile)
            elif target_variable.upper() in ["J_H2O", "FLUX"]:
                y_data = np.interp(z_eval, res.z_grid, res.j_h2o_flux_profile * 1e4) # x1e-4
            elif target_variable.upper() in ["CO2_CONVERSION"]:
                # Local conversion along z: (F_CO2_0 - F_CO2(z))/F_CO2_0
                conv_z = (res.F_CO2[0] - res.F_CO2) / res.F_CO2[0] * 100.0
                y_data = np.interp(z_eval, res.z_grid, conv_z)
            else:
                y_data = np.interp(z_eval, res.z_grid, res.y_CH3OH * 100.0)
        else:
            y_data = np.zeros(n_points_z)

        target_matrix[i, :] = y_data

    Z_grid, Param_grid = np.meshgrid(z_eval, parameter_values)
    title_str = f"1D-Derived Pseudo-2D Reactor Performance Map\nTarget: {target_variable} vs {parameter_name}"
    return Z_grid, Param_grid, target_matrix, title_str


def plot_reactor_geometry(save_path: Optional[str] = None) -> plt.Figure:
    """
    Renders an engineering longitudinal cross-section schematic of the tube-in-tube membrane reactor.
    """
    setup_matplotlib_style()
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    
    # Outer reactor tube (shell)
    ax.fill_between([0, 10], [3, 3], [4, 4], color="#f1f5f9", edgecolor="#475569", linewidth=1.5, label="Sweep Channel (Shell)")
    ax.fill_between([0, 10], [-4, -4], [-3, -3], color="#f1f5f9", edgecolor="#475569", linewidth=1.5)
    
    # Selective Membrane layer (NaA Zeolite on Ceramic Support)
    ax.fill_between([1, 9], [2.2, 2.2], [2.5, 2.5], color="#fde047", edgecolor="#ca8a04", hatch="//", label="NaA Zeolite Membrane")
    ax.fill_between([1, 9], [-2.5, -2.5], [-2.2, -2.2], color="#fde047", edgecolor="#ca8a04", hatch="//")
    
    # Inner Reaction Zone (Packed with CZA catalyst)
    ax.fill_between([0, 10], [-2.2, -2.2], [2.2, 2.2], color="#dbeafe", edgecolor="#2563eb", alpha=0.6, label="Reaction Zone (CZA Packed Bed)")

    # Flow arrows
    # Synthesis Gas Feed (Left to Right)
    ax.annotate("Feed Gas (CO2 + H2) ->\nT_in = 200-250 C, P = 30-80 bar", xy=(0.2, 0), xytext=(-3.5, 0),
                arrowprops=dict(arrowstyle="->", color="#1e293b", lw=2),
                fontsize=10, fontweight="bold", va="center", color="#1e293b")
    
    # Products Outlet
    ax.annotate("-> Products (CH3OH + CO + unreacted)\nTo separator / condenser", xy=(9.8, 0), xytext=(10.3, 0),
                arrowprops=dict(arrowstyle="<-", color="#10b981", lw=2),
                fontsize=10, fontweight="bold", va="center", color="#10b981")

    # Sweep Gas (Counter-Current: Right to Left)
    ax.annotate("<- Sweep Gas (N2)", xy=(8.5, 3.5), xytext=(10.3, 3.5),
                arrowprops=dict(arrowstyle="->", color="#64748b", lw=1.8),
                fontsize=9, fontweight="bold", va="center", color="#475569")
    ax.annotate("Sweep + Permeated H2O <-", xy=(1.5, 3.5), xytext=(-3.5, 3.5),
                arrowprops=dict(arrowstyle="<-", color="#ef4444", lw=1.8),
                fontsize=9, fontweight="bold", va="center", color="#ef4444")

    # Membrane Permeation arrows (H2O escaping radially)
    for x in np.linspace(2.5, 7.5, 5):
        ax.annotate("", xy=(x, 2.9), xytext=(x, 1.8),
                    arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.8))
        ax.annotate("", xy=(x, -2.9), xytext=(x, -1.8),
                    arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.8))
    
    ax.text(5.0, 1.2, "CO2 + 3H2 <=> CH3OH + H2O (Exothermic)\nCO2 + H2 <=> CO + H2O (RWGS)",
            ha="center", va="center", fontsize=9, fontweight="bold", color="#1e3a8a",
            bbox=dict(boxstyle="round,pad=0.3", fc="#ffffff", ec="#93c5fd", lw=1))

    ax.text(5.0, 2.7, "Selective H2O Permeation (J_H2O)", ha="center", va="center", fontsize=8, color="#ef4444", fontweight="bold")

    ax.set_xlim(-4.0, 14.0)
    ax.set_ylim(-5.0, 5.0)
    ax.axis("off")
    ax.set_title("Reduced-Order Membrane Reactor Geometry (Tube-in-Tube Counter-Current)", fontsize=12, fontweight="bold", pad=15, color="#1e293b")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig


def generate_publication_figures(output_dir: str = "results/figures"):
    """
    Generates all 15 publication-grade research figures.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    setup_matplotlib_style()

    print("=== Generating 15 Publication-Grade Figures ===")

    # Run reference MR and TR simulations
    res_mr = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0, membrane_enabled=True, water_permeance=1.5e-7)
    res_tr = simulate_reactor(temperature=493.15, pressure=50.0, total_flow=0.015, h2_co2_ratio=3.0, membrane_enabled=False)

    # Figure 1: Temperature Profile (MR vs TR)
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(res_mr.z_grid, res_mr.T_profile - 273.15, color=COLORS["emerald"], lw=2.2, label="Membrane Reactor (MR)")
    ax.plot(res_tr.z_grid, res_tr.T_profile - 273.15, color=COLORS["slate"], lw=2.0, ls="--", label="Conventional Packed Bed (TR)")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Bed Temperature (°C)")
    ax.set_title("Axial Temperature Profile in Non-Isothermal Packed Bed")
    ax.grid(True)
    ax.legend(frameon=True)
    fig.savefig(out / "01_temperature_profile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: Species Profiles (Mole Fractions)
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    ax.plot(res_mr.z_grid, res_mr.y_CO2 * 100, color=COLORS["co2"], lw=2.0, label="CO2")
    ax.plot(res_mr.z_grid, res_mr.y_H2 * 100, color=COLORS["h2"], lw=2.0, label="H2")
    ax.plot(res_mr.z_grid, res_mr.y_CH3OH * 100, color=COLORS["meoh"], lw=2.2, label="CH3OH (Methanol)")
    ax.plot(res_mr.z_grid, res_mr.y_H2O * 100, color=COLORS["h2o"], lw=2.0, label="H2O")
    ax.plot(res_mr.z_grid, res_mr.y_CO * 100, color=COLORS["co"], lw=1.8, ls=":", label="CO")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Mole Fraction (mol %)")
    ax.set_title("Axial Gas Phase Composition Profile (MR Mode)")
    ax.grid(True)
    ax.legend(frameon=True)
    fig.savefig(out / "02_species_profiles.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figure 3: Reaction Rates vs Reactor Length
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(res_mr.z_grid, res_mr.r_meoh_profile, color=COLORS["emerald"], lw=2.2, label="r_MeOH (Methanol Synthesis)")
    ax.plot(res_mr.z_grid, res_mr.r_rwgs_profile, color=COLORS["amber"], lw=2.0, label="r_RWGS (Reverse Water-Gas Shift)")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Reaction Rate [mol / (kg_cat · s)]")
    ax.set_title("Intrinsic LHHW Reaction Rate Distribution")
    ax.grid(True)
    ax.legend(frameon=True)
    fig.savefig(out / "03_reaction_rates.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figure 4: Membrane Flux Profile
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(res_mr.z_grid, res_mr.j_h2o_flux_profile * 1e4, color=COLORS["red"], lw=2.2)
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("H2O Permeation Flux J_H2O [10⁻⁴ mol / (m² · s)]")
    ax.set_title("Selective H2O Membrane Flux Distribution")
    ax.grid(True)
    fig.savefig(out / "04_membrane_flux.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figure 5: H2O Removal & Accumulation
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(res_mr.z_grid, res_mr.cumulative_h2o_removed * 1e5, color=COLORS["red"], lw=2.2, label="Cumulative H2O Removed (mol/s × 10⁵)")
    ax.plot(res_mr.z_grid, res_mr.F_H2O * 1e5, color=COLORS["cyan"], lw=2.0, ls="--", label="Remaining Tube H2O Flow (mol/s × 10⁵)")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Molar Flow Rate [10⁻⁵ mol/s]")
    ax.set_title("Water Removal Dynamics along Membrane Tube")
    ax.grid(True)
    ax.legend(frameon=True)
    fig.savefig(out / "05_h2o_removal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figures 6, 7, 8, 9: 2D Pseudo-Contour Performance Maps
    # 06: Temperature - Length contour for CH3OH
    temps = np.linspace(463.15, 523.15, 20)
    Z_T, P_T, M_T, _ = generate_reactor_contour("temperature", temps, "CH3OH")
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    cf = ax.contourf(Z_T, P_T - 273.15, M_T, levels=25, cmap="viridis")
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Methanol Mole Fraction (%)")
    ax.set_xlabel("Reactor Axial Position z (m)")
    ax.set_ylabel("Inlet Temperature (°C)")
    ax.set_title("1D-Derived Pseudo-2D Reactor Performance Map\n(CH3OH Mole Fraction vs Axial Length & Temperature)")
    fig.savefig(out / "06_temperature_pressure_map.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 07: Pressure - Length contour for CO2 Conversion
    pressures = np.linspace(30.0, 80.0, 20)
    Z_P, P_P, M_P, _ = generate_reactor_contour("pressure", pressures, "CO2_CONVERSION")
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    cf = ax.contourf(Z_P, P_P, M_P, levels=25, cmap="magma")
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("CO2 Conversion (%)")
    ax.set_xlabel("Reactor Axial Position z (m)")
    ax.set_ylabel("Operating Pressure (bar)")
    ax.set_title("1D-Derived Pseudo-2D Reactor Performance Map\n(CO2 Conversion vs Axial Length & Operating Pressure)")
    fig.savefig(out / "07_temperature_gHSV_map.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 08: Flow - Permeance sweep for H2O Removal
    permeances = np.linspace(0.2e-7, 3.0e-7, 20)
    Z_perm, P_perm, M_perm, _ = generate_reactor_contour("water_permeance", permeances, "H2O")
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    cf = ax.contourf(Z_perm, P_perm * 1e7, M_perm, levels=25, cmap="coolwarm")
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Tube H2O Mole Fraction (%)")
    ax.set_xlabel("Reactor Axial Position z (m)")
    ax.set_ylabel("Water Permeance (10⁻⁷ mol/(m²·s·Pa))")
    ax.set_title("1D-Derived Pseudo-2D Water Depletion Map")
    fig.savefig(out / "08_pressure_SF_map.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 09: Geometry Schematic
    plot_reactor_geometry(save_path=str(out / "09_membrane_area_map.png"))

    # 10: Conversion Contour
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    cf = ax.contourf(Z_T, P_T - 273.15, M_T, levels=20, cmap="cividis")
    fig.colorbar(cf, ax=ax, label="MeOH (%)")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Inlet Temperature (°C)")
    ax.set_title("Methanol Yield Spatial Landscape")
    fig.savefig(out / "10_conversion_contour.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 11: Methanol Yield Contour
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    cf = ax.contourf(Z_P, P_P, M_P, levels=20, cmap="plasma")
    fig.colorbar(cf, ax=ax, label="CO2 Conversion (%)")
    ax.set_xlabel("Axial Position z (m)")
    ax.set_ylabel("Pressure (bar)")
    ax.set_title("CO2 Conversion Spatial Map")
    fig.savefig(out / "11_methanol_yield_contour.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Figures 01-11 generated successfully.")
