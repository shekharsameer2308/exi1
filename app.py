"""
E-Methanol Membrane Reactor Engineering Dashboard.
Physics Engine, Validation, DOE, ML Surrogate, Contours, Full-Length Industrial Design, and Optimization.
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from pathlib import Path

from src.emethanol.reactor import simulate_reactor, MembraneReactor1D, ModelConfig, ReactorSimulationResult
from src.emethanol.design import design_full_length_reactor, IndustrialReactorDesignResult
from src.emethanol.visualization import (
    generate_reactor_contour,
    plot_reactor_geometry,
    setup_matplotlib_style,
    COLORS,
)
from src.emethanol.optimization import optimize_reactor_physics, is_in_training_domain

# Page Configuration
st.set_page_config(page_title="E-Methanol Membrane Reactor Engineering System", layout="wide")

# Minimalist Muted Styling conforming to project rules
st.markdown(
    """
<style>
    h1, h2, h3, h4 { color: #475569; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .content-card { 
        background-color: #f8fafc; border: 1px solid #e2e8f0; 
        padding: 1.25rem; border-radius: 0.5rem; color: #475569; margin-bottom: 1rem;
    }
    .metric-value { color: #10b981; font-size: 2.2rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-value-slate { color: #475569; font-size: 2.2rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-value-red { color: #ef4444; font-size: 2.2rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-label { font-size: 0.85rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .neutral-badge {
        background-color: #e2e8f0; color: #475569; padding: 0.2rem 0.5rem;
        border-radius: 0.25rem; font-size: 0.8rem; font-weight: 600;
    }
    .disclaimer-badge {
        background-color: #fef3c7; color: #92400e; padding: 0.4rem 0.8rem;
        border-radius: 0.35rem; font-size: 0.85rem; font-weight: 600; border: 1px solid #fde68a;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_surrogate_model():
    """Loads serialized ML surrogate model."""
    path = Path("surrogate_rf.joblib")
    if path.exists():
        return joblib.load(path)
    return None


surrogate_model = load_surrogate_model()

# Header
st.title("E-Methanol Membrane Reactor Engineering System")
st.caption("Scientific Reaction Engineering, Multicomponent Transport, Full-Length Industrial Sizing, and Surrogate Acceleration Framework")

# 10 Engineering Tabs
tabs = st.tabs([
    "Overview",
    "Reactor Simulation",
    "Axial Profiles",
    "Reactor Contours",
    "Parameter Sweeps",
    "Industrial Sizing",
    "Optimization",
    "ML Surrogate",
    "Physics vs ML",
    "Validation & Diagnostics",
])


# ==========================================
# TAB 1: OVERVIEW
# ==========================================
with tabs[0]:
    st.subheader("System Overview & Reference Alignment")
    
    col_ov1, col_ov2 = st.columns([3, 2])
    with col_ov1:
        st.markdown(
            """
        <div class="content-card">
            <h4>Direct CO2 Hydrogenation to E-Methanol</h4>
            <p>This engineering platform simulates, sizes, and optimizes full-length non-isothermal catalytic membrane reactors for synthetic e-methanol production:</p>
            <ul>
                <li><strong>Methanol Synthesis:</strong> CO2 + 3H2 ⇌ CH3OH + H2O (ΔH°298 = -49.5 kJ/mol)</li>
                <li><strong>Reverse Water-Gas Shift:</strong> CO2 + H2 ⇌ CO + H2O (ΔH°298 = +41.2 kJ/mol)</li>
                <li><strong>In-Situ Selective Dehydration:</strong> Hydrophilic NaA-zeolite membrane selectively extracts byproduct H2O, bypassing thermodynamic equilibrium barriers (Le Chatelier's principle).</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_ov2:
        st.markdown(
            """
        <div class="content-card">
            <h4>Scientific Reference Alignment</h4>
            <p><strong>Primary Literature:</strong> <em>Energy Advances</em> (2025) - "Design parameter optimization of a membrane reactor for methanol synthesis using a sophisticated CFD model".</p>
            <p><span class="neutral-badge">Model Classification: Level 2 / Level 3 1D Membrane Reactor</span></p>
            <p style="font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;">
                Stiff ODE integration (BDF/Radau), LHHW kinetics (VBF & Mignard-Pritchard), non-isothermal energy balances, multi-tubular bundle sizing, and automated elemental conservation verification.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.subheader("Reactor Geometry Schematic")
    fig_geom = plot_reactor_geometry()
    st.pyplot(fig_geom)
    plt.close(fig_geom)


# ==========================================
# TAB 2: REACTOR SIMULATION
# ==========================================
with tabs[1]:
    st.subheader("Deterministic 1D Reactor Simulation")

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        sim_T = st.slider("Inlet Temperature T_in (K)", 453.15, 543.15, 493.15, 1.0, help="220 °C = 493.15 K")
        sim_P = st.slider("Operating Pressure P_in (bar)", 20.0, 80.0, 50.0, 1.0)
        sim_ratio = st.slider("H2 / CO2 Feed Ratio", 2.0, 5.0, 3.0, 0.1)
    with col_in2:
        sim_flow = st.slider("Inlet Feed Flow (mol/s)", 0.005, 0.080, 0.015, 0.001)
        sim_perm = st.slider("H2O Permeance (10⁻⁷ mol/(m²·s·Pa))", 0.0, 4.0, 1.5, 0.1) * 1e-7
        sim_L = st.slider("Reactor Length (m)", 0.5, 8.0, 1.0, 0.1, help="Bench (1m), Pilot (3m), Industrial Full-Length (6m)")
    with col_in3:
        sim_D = st.slider("Tube Diameter (m)", 0.01, 0.06, 0.02, 0.002)
        sim_kin = st.selectbox("Kinetic Formulation", ["VBF", "MIGNARD_PRITCHARD"])
        sim_mem_model = st.selectbox("Membrane Model", ["LDF", "MAXWELL_STEFAN"])
        sim_mr_mode = st.checkbox("Membrane Active (MR vs TR)", value=True)
        sim_thermal = st.checkbox("Non-Isothermal Heat Balance", value=True)
        sim_ergun = st.checkbox("Packed Bed Pressure Drop (Ergun)", value=True)

    # Run deterministic simulation
    res_sim = simulate_reactor(
        temperature=sim_T,
        pressure=sim_P,
        total_flow=sim_flow,
        h2_co2_ratio=sim_ratio,
        water_permeance=sim_perm,
        reactor_length=sim_L,
        reactor_diameter=sim_D,
        kinetic_model=sim_kin,
        membrane_model=sim_mem_model,
        membrane_enabled=sim_mr_mode,
        non_isothermal=sim_thermal,
        pressure_drop=sim_ergun,
    )

    # Run TR benchmark for direct comparison
    res_tr_bench = simulate_reactor(
        temperature=sim_T,
        pressure=sim_P,
        total_flow=sim_flow,
        h2_co2_ratio=sim_ratio,
        reactor_length=sim_L,
        reactor_diameter=sim_D,
        kinetic_model=sim_kin,
        membrane_enabled=False,
        non_isothermal=sim_thermal,
        pressure_drop=sim_ergun,
    )

    st.markdown("---")
    st.subheader("Performance Metrics (MR vs Conventional TR Benchmark)")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">CO2 Conversion</div>
            <div class="metric-value">{res_sim.co2_conversion * 100:.2f}%</div>
            <div style="font-size: 0.8rem; color: #6b7280;">TR Baseline: {res_tr_bench.co2_conversion * 100:.2f}%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Methanol Yield</div>
            <div class="metric-value">{res_sim.meoh_yield * 100:.2f}%</div>
            <div style="font-size: 0.8rem; color: #6b7280;">TR Baseline: {res_tr_bench.meoh_yield * 100:.2f}%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with m_col3:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Methanol Selectivity</div>
            <div class="metric-value">{res_sim.meoh_selectivity * 100:.2f}%</div>
            <div style="font-size: 0.8rem; color: #6b7280;">TR Baseline: {res_tr_bench.meoh_selectivity * 100:.2f}%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with m_col4:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">H2O Removal Fraction</div>
            <div class="metric-value-red">{res_sim.h2o_removal_fraction * 100:.2f}%</div>
            <div style="font-size: 0.8rem; color: #6b7280;">Extracted into sweep stream</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ==========================================
# TAB 3: AXIAL PROFILES
# ==========================================
with tabs[2]:
    st.subheader(f"Spatial 1D Axial Profiles (Full Length L = {sim_L:.1f} m)")
    setup_matplotlib_style()

    p_type = st.radio("Display Mode", ["Mole Fractions (mol %)", "Molar Flow Rates (mol/s)", "Thermal & Kinetic Profiles"], horizontal=True)

    if p_type == "Mole Fractions (mol %)":
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
        ax.plot(res_sim.z_grid, res_sim.y_CO2 * 100, color=COLORS["co2"], lw=2, label="CO2")
        ax.plot(res_sim.z_grid, res_sim.y_H2 * 100, color=COLORS["h2"], lw=2, label="H2")
        ax.plot(res_sim.z_grid, res_sim.y_CH3OH * 100, color=COLORS["meoh"], lw=2.5, label="CH3OH (Methanol)")
        ax.plot(res_sim.z_grid, res_sim.y_H2O * 100, color=COLORS["h2o"], lw=2, label="H2O")
        ax.plot(res_sim.z_grid, res_sim.y_CO * 100, color=COLORS["co"], lw=1.8, ls=":", label="CO")
        ax.set_xlabel("Axial Position z (m)")
        ax.set_ylabel("Gas Mole Fraction (mol %)")
        ax.set_title(f"Axial Composition Trajectories across {sim_L:.1f} m Bed Length")
        ax.grid(True)
        ax.legend(frameon=True)
        st.pyplot(fig)
        plt.close(fig)

    elif p_type == "Molar Flow Rates (mol/s)":
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
        ax.plot(res_sim.z_grid, res_sim.F_CO2 * 1000, color=COLORS["co2"], lw=2, label="F_CO2 (mmol/s)")
        ax.plot(res_sim.z_grid, res_sim.F_H2 * 1000, color=COLORS["h2"], lw=2, label="F_H2 (mmol/s)")
        ax.plot(res_sim.z_grid, res_sim.F_CH3OH * 1000, color=COLORS["meoh"], lw=2.5, label="F_CH3OH (mmol/s)")
        ax.plot(res_sim.z_grid, res_sim.F_H2O * 1000, color=COLORS["h2o"], lw=2, label="F_H2O (mmol/s)")
        ax.plot(res_sim.z_grid, res_sim.cumulative_h2o_removed * 1000, color=COLORS["red"], lw=2, ls="--", label="Permeated H2O (mmol/s)")
        ax.set_xlabel("Axial Position z (m)")
        ax.set_ylabel("Molar Flow Rate (mmol/s)")
        ax.set_title(f"Species Mass Flow Rates & Water Permeation (L = {sim_L:.1f} m)")
        ax.grid(True)
        ax.legend(frameon=True)
        st.pyplot(fig)
        plt.close(fig)

    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
        ax1.plot(res_sim.z_grid, res_sim.T_profile - 273.15, color=COLORS["temp"], lw=2.2)
        ax1.set_xlabel("Axial Position z (m)")
        ax1.set_ylabel("Bed Temperature (°C)")
        ax1.set_title("Axial Bed Temperature Profile")
        ax1.grid(True)

        ax2.plot(res_sim.z_grid, res_sim.r_meoh_profile, color=COLORS["emerald"], lw=2, label="r_MeOH")
        ax2.plot(res_sim.z_grid, res_sim.r_rwgs_profile, color=COLORS["amber"], lw=2, label="r_RWGS")
        ax2.set_xlabel("Axial Position z (m)")
        ax2.set_ylabel("Reaction Rate [mol/(kg_cat·s)]")
        ax2.set_title("Intrinsic LHHW Reaction Rates")
        ax2.grid(True)
        ax2.legend(frameon=True)
        st.pyplot(fig)
        plt.close(fig)


# ==========================================
# TAB 4: REACTOR CONTOURS
# ==========================================
with tabs[3]:
    st.subheader("1D-Derived Pseudo-2D Reactor Performance Maps")
    st.markdown(
        '<div class="disclaimer-badge">Note: 1D-derived pseudo-2D reactor contour — not a 2D/3D CFD solution. Generated by integrating multiple 1D axial ODE runs.</div>',
        unsafe_allow_html=True,
    )

    c_col1, c_col2 = st.columns(2)
    with c_col1:
        sweep_param = st.selectbox("Swept Dimension (Y-Axis)", ["temperature", "pressure", "water_permeance", "total_flow", "h2_co2_ratio"])
    with c_col2:
        target_var = st.selectbox("Contour Target Variable (Color Field)", ["CH3OH", "CO2_CONVERSION", "H2O", "temperature", "R_MEOH", "J_H2O"])

    if sweep_param == "temperature":
        vals = np.linspace(463.15, 533.15, 20)
    elif sweep_param == "pressure":
        vals = np.linspace(25.0, 80.0, 20)
    elif sweep_param == "water_permeance":
        vals = np.linspace(0.2e-7, 3.0e-7, 20)
    elif sweep_param == "total_flow":
        vals = np.linspace(0.008, 0.050, 20)
    else:
        vals = np.linspace(2.2, 4.5, 20)

    Z_g, P_g, M_g, title_txt = generate_reactor_contour(
        parameter_name=sweep_param,
        parameter_values=vals,
        target_variable=target_var,
        fixed_conditions={"temperature": sim_T, "pressure": sim_P, "h2_co2_ratio": sim_ratio, "water_permeance": sim_perm, "reactor_length": sim_L},
    )

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    y_axis_vals = P_g - 273.15 if sweep_param == "temperature" else (P_g * 1e7 if sweep_param == "water_permeance" else P_g)
    y_unit = "Inlet Temperature (°C)" if sweep_param == "temperature" else ("Permeance (10⁻⁷ mol/(m²·s·Pa))" if sweep_param == "water_permeance" else sweep_param)
    
    cf = ax.contourf(Z_g, y_axis_vals, M_g, levels=25, cmap="viridis")
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label(f"{target_var}")
    ax.set_xlabel("Reactor Axial Length z (m)")
    ax.set_ylabel(y_unit)
    ax.set_title(title_txt)
    st.pyplot(fig)
    plt.close(fig)


# ==========================================
# TAB 5: PARAMETER SWEEPS
# ==========================================
with tabs[4]:
    st.subheader("Engineering Parameter Sweeps & Response Surfaces")
    
    sw_choice = st.selectbox("Select Parameter Sweep Analysis", [
        "Temperature Sweep (200 - 260 °C)",
        "Pressure Sweep (20 - 80 bar)",
        "Flow Rate / GHSV Sweep",
        "Membrane Permeance Sweep (MR vs TR)",
    ])

    if sw_choice == "Temperature Sweep (200 - 260 °C)":
        sw_temps = np.linspace(473.15, 533.15, 20)
        yields, convs, sels = [], [], []
        for T in sw_temps:
            r = simulate_reactor(temperature=float(T), pressure=sim_P, total_flow=sim_flow, h2_co2_ratio=sim_ratio, water_permeance=sim_perm, reactor_length=sim_L)
            yields.append(r.meoh_yield * 100)
            convs.append(r.co2_conversion * 100)
            sels.append(r.meoh_selectivity * 100)
        
        fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
        ax.plot(sw_temps - 273.15, yields, color=COLORS["emerald"], lw=2.2, label="Methanol Yield (%)")
        ax.plot(sw_temps - 273.15, convs, color=COLORS["slate"], lw=2, ls="--", label="CO2 Conversion (%)")
        ax.plot(sw_temps - 273.15, sels, color=COLORS["cyan"], lw=2, ls=":", label="Methanol Selectivity (%)")
        ax.set_xlabel("Inlet Temperature (°C)")
        ax.set_ylabel("Percentage (%)")
        ax.set_title("Temperature Sensitivity (Kinetic Activation vs Equilibrium Reversal)")
        ax.grid(True)
        ax.legend(frameon=True)
        st.pyplot(fig)
        plt.close(fig)

    elif sw_choice == "Pressure Sweep (20 - 80 bar)":
        sw_press = np.linspace(20.0, 80.0, 20)
        yields, convs = [], []
        for P in sw_press:
            r = simulate_reactor(temperature=sim_T, pressure=float(P), total_flow=sim_flow, h2_co2_ratio=sim_ratio, water_permeance=sim_perm, reactor_length=sim_L)
            yields.append(r.meoh_yield * 100)
            convs.append(r.co2_conversion * 100)
        
        fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
        ax.plot(sw_press, yields, color=COLORS["emerald"], lw=2.2, label="Methanol Yield (%)")
        ax.plot(sw_press, convs, color=COLORS["slate"], lw=2, ls="--", label="CO2 Conversion (%)")
        ax.set_xlabel("Operating Pressure (bar)")
        ax.set_ylabel("Percentage (%)")
        ax.set_title("Pressure Dependency (Le Chatelier Shift)")
        ax.grid(True)
        ax.legend(frameon=True)
        st.pyplot(fig)
        plt.close(fig)

    elif sw_choice == "Membrane Permeance Sweep (MR vs TR)":
        sw_perms = np.linspace(0.0, 3.0e-7, 20)
        yields, h2o_rems = [], []
        for q in sw_perms:
            r = simulate_reactor(temperature=sim_T, pressure=sim_P, total_flow=sim_flow, water_permeance=float(q), membrane_enabled=(q > 0), reactor_length=sim_L)
            yields.append(r.meoh_yield * 100)
            h2o_rems.append(r.h2o_removal_fraction * 100)
        
        fig, ax1 = plt.subplots(figsize=(8, 4), dpi=300)
        ax2 = ax1.twinx()
        ax1.plot(sw_perms * 1e7, yields, color=COLORS["emerald"], lw=2.2, label="Methanol Yield (%)")
        ax2.plot(sw_perms * 1e7, h2o_rems, color=COLORS["red"], lw=2, ls="--", label="H2O Removal (%)")
        ax1.set_xlabel("Water Permeance (10⁻⁷ mol/(m²·s·Pa))")
        ax1.set_ylabel("Methanol Yield (%)", color=COLORS["emerald"])
        ax2.set_ylabel("H2O Removal Fraction (%)", color=COLORS["red"])
        ax1.set_title("Impact of Membrane Permeance on Equilibrium Dehydration")
        ax1.grid(True)
        st.pyplot(fig)
        plt.close(fig)


# ==========================================
# TAB 6: INDUSTRIAL SIZING & FULL-LENGTH DESIGN
# ==========================================
with tabs[5]:
    st.subheader("Full-Length Industrial Multi-Tubular Reactor Design & Sizing")
    st.markdown("Scale up from single-tube 1D physics to multi-thousand tube industrial reactor bundles.")

    col_ds1, col_ds2, col_ds3 = st.columns(3)
    with col_ds1:
        target_tpd = st.number_input("Target Methanol Capacity (Metric Tons / Day)", min_value=0.1, max_value=2000.0, value=100.0, step=10.0)
        ind_L = st.slider("Industrial Tube Length (m)", 3.0, 8.0, 6.0, 0.5)
    with col_ds2:
        ind_Dt = st.slider("Tube Inner Diameter (mm)", 20.0, 50.0, 38.0, 2.0) * 1e-3
        ind_flow_tube = st.slider("Flow per Tube (mol/s)", 0.010, 0.100, 0.040, 0.005)
    with col_ds3:
        ind_T = st.slider("Inlet Temp (°C)", 200.0, 260.0, 230.0, 5.0) + 273.15
        ind_P = st.slider("Inlet Pressure (bar)", 30.0, 80.0, 60.0, 5.0)

    # Calculate full-length multi-tubular design
    design_res = design_full_length_reactor(
        target_production_tpd=target_tpd,
        tube_length=ind_L,
        tube_diameter=ind_Dt,
        temperature=ind_T,
        pressure=ind_P,
        single_tube_flow=ind_flow_tube,
        h2_co2_ratio=sim_ratio,
        water_permeance=sim_perm,
    )

    st.markdown("---")
    st.subheader(f"Multi-Tubular Bundle Specifications ({target_tpd:.0f} TPD Methanol Plant)")

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Number of Tubes</div>
            <div class="metric-value-slate">{design_res.number_of_tubes:,}</div>
            <div style="font-size: 0.8rem; color: #6b7280;">Shell Diameter: {design_res.shell_diameter_m:.2f} m</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with d_col2:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Total Catalyst Mass</div>
            <div class="metric-value">{design_res.total_catalyst_mass_tonnes:.2f} t</div>
            <div style="font-size: 0.8rem; color: #6b7280;">Bed Volume: {design_res.reactor_total_volume_m3:.1f} m³</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with d_col3:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Total Membrane Area</div>
            <div class="metric-value">{design_res.total_membrane_area_m2:.1f} m²</div>
            <div style="font-size: 0.8rem; color: #6b7280;">Area/Vol: {design_res.membrane_area_to_volume_ratio:.1f} m²/m³</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with d_col4:
        st.markdown(
            f"""
        <div class="content-card">
            <div class="metric-label">Electrolyzer Power</div>
            <div class="metric-value-red">{design_res.electrolyzer_power_mw:.1f} MW</div>
            <div style="font-size: 0.8rem; color: #6b7280;">H2 Feed: {design_res.h2_feed_tpd:.1f} TPD</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Detailed Material & Energy Balance Table
    st.subheader("Plant Material & Energy Balance Summary")
    df_bal = pd.DataFrame([
        {"Parameter": "Methanol Production", "Value": f"{design_res.actual_production_tpd:.1f}", "Unit": "TPD (Metric Tons/Day)"},
        {"Parameter": "CO2 Feedstock Required", "Value": f"{design_res.co2_feed_tpd:.1f}", "Unit": "TPD"},
        {"Parameter": "Green H2 Required", "Value": f"{design_res.h2_feed_tpd:.1f}", "Unit": "TPD"},
        {"Parameter": "H2O Extracted via Membrane", "Value": f"{design_res.water_extracted_membrane_tpd:.1f}", "Unit": "TPD"},
        {"Parameter": "Reactor Cooling Duty (Steam Gen)", "Value": f"{design_res.cooling_duty_mw:.2f}", "Unit": "MW (Thermal)"},
        {"Parameter": "Gas Hourly Space Velocity (GHSV)", "Value": f"{design_res.ghsv_h_inv:.0f}", "Unit": "h⁻¹"},
        {"Parameter": "Bed Pressure Drop (Ergun)", "Value": f"{design_res.pressure_drop_bar:.2f}", "Unit": "bar"},
    ])
    st.dataframe(df_bal, use_container_width=True)


# ==========================================
# TAB 7: OPTIMIZATION
# ==========================================
with tabs[6]:
    st.subheader("Constrained Reactor Optimization (Physics-Engine Verified)")
    st.markdown("Automated constrained optimization targeting maximum methanol yield with strict physics verification.")

    if st.button("Execute Constrained Optimization", type="primary"):
        with st.spinner("Optimizing operational state with physics verification..."):
            opt_out = optimize_reactor_physics(
                objective="max_yield",
                min_selectivity=0.85,
                surrogate_model=surrogate_model,
            )

            st.success("Optimization completed with verified deterministic physics!")

            oc = opt_out["optimal_conditions"]
            phys = opt_out["physics_result"]

            col_o1, col_o2, col_o3 = st.columns(3)
            with col_o1:
                st.markdown(
                    f"""
                <div class="content-card">
                    <h4>Optimal Operating Conditions</h4>
                    <p><strong>Temperature:</strong> {oc['T_in_K']:.1f} K ({oc['T_in_K']-273.15:.1f} °C)</p>
                    <p><strong>Pressure:</strong> {oc['P_in_bar']:.1f} bar</p>
                    <p><strong>Feed Flow:</strong> {oc['flow_mol_s']:.4f} mol/s</p>
                    <p><strong>H2/CO2 Ratio:</strong> {oc['h2_co2_ratio']:.2f}</p>
                    <p><strong>Permeance:</strong> {oc['water_permeance']*1e7:.2f} × 10⁻⁷</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with col_o2:
                st.markdown(
                    f"""
                <div class="content-card">
                    <h4>Verified Physics Output</h4>
                    <p><strong>CO2 Conversion:</strong> {phys['co2_conversion']*100:.2f}%</p>
                    <p><strong>Methanol Yield:</strong> {phys['meoh_yield']*100:.2f}%</p>
                    <p><strong>Methanol Selectivity:</strong> {phys['meoh_selectivity']*100:.2f}%</p>
                    <p><strong>H2O Removal:</strong> {phys['h2o_removal_fraction']*100:.2f}%</p>
                    <p><strong>Outlet Temp:</strong> {phys['outlet_temperature']-273.15:.1f} °C</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with col_o3:
                in_dom, dom_msg = is_in_training_domain(oc)
                st.markdown(
                    f"""
                <div class="content-card">
                    <h4>Verification Diagnostics</h4>
                    <p><strong>Optimization Status:</strong> {opt_out['optimization_message']}</p>
                    <p><strong>Carbon Balance Error:</strong> {phys['carbon_balance_error']:.2e}</p>
                    <p><strong>Physical Plausibility:</strong> {phys['validation_message']}</p>
                    <p><strong>Domain Status:</strong> <span class="neutral-badge">{dom_msg}</span></p>
                </div>
                """,
                    unsafe_allow_html=True,
                )


# ==========================================
# TAB 8: ML SURROGATE
# ==========================================
with tabs[7]:
    st.subheader("Machine Learning Surrogate Predictor")

    if surrogate_model is not None:
        inputs_surr = {
            "T_in_K": sim_T,
            "P_in_bar": sim_P,
            "flow_mol_s": sim_flow,
            "h2_co2_ratio": sim_ratio,
            "water_permeance": sim_perm,
        }
        in_dom, dom_msg = is_in_training_domain(inputs_surr)
        if not in_dom:
            st.warning(f"⚠️ {dom_msg}")

        X_df = pd.DataFrame([inputs_surr])
        preds = surrogate_model.predict(X_df)[0]

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Surrogate CO2 Conv", f"{preds[0]*100:.2f}%")
        with col_s2:
            st.metric("Surrogate MeOH Yield", f"{preds[1]*100:.2f}%")
        with col_s3:
            st.metric("Surrogate Selectivity", f"{preds[2]*100:.2f}%" if len(preds) > 2 else "N/A")
        with col_s4:
            st.metric("Surrogate H2O Removal", f"{preds[3]*100:.2f}%" if len(preds) > 3 else "N/A")

        st.markdown("---")
        st.subheader("Feature Importance")
        imp_path = Path("results/figures/14_feature_importance.png")
        if imp_path.exists():
            st.image(str(imp_path))
    else:
        st.info("Surrogate model not yet trained. Run scripts/04_train_surrogate.py.")


# ==========================================
# TAB 9: PHYSICS VS ML
# ==========================================
with tabs[8]:
    st.subheader("Physics Engine vs ML Surrogate Parity Benchmark")
    
    col_par1, col_par2 = st.columns(2)
    with col_par1:
        par_img = Path("results/figures/12_surrogate_parity.png")
        if par_img.exists():
            st.image(str(par_img), caption="Parity Plots (Physics vs ML)")
    with col_par2:
        res_img = Path("results/figures/13_surrogate_residuals.png")
        if res_img.exists():
            st.image(str(res_img), caption="Error Residuals Distribution")

    metrics_csv = Path("results/ml_metrics.csv")
    if metrics_csv.exists():
        st.markdown("### Per-Target Multi-Model Evaluation Metrics")
        df_m = pd.read_csv(metrics_csv)
        st.dataframe(df_m, use_container_width=True)


# ==========================================
# TAB 10: VALIDATION & DIAGNOSTICS
# ==========================================
with tabs[9]:
    st.subheader("Validation Test Diagnostics & Conservation Verification")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(
            f"""
        <div class="content-card">
            <h4>Elemental Conservation Balances (Current Simulation)</h4>
            <p><strong>Carbon Balance Error:</strong> {res_sim.carbon_balance_error:.3e} (< 1e-4 required)</p>
            <p><strong>Hydrogen Balance Error:</strong> {res_sim.hydrogen_balance_error:.3e} (< 1e-4 required)</p>
            <p><strong>Oxygen Balance Error:</strong> {res_sim.oxygen_balance_error:.3e} (< 1e-4 required)</p>
            <p><strong>Physics Validation Status:</strong> <span class="neutral-badge">{res_sim.validation_message}</span></p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_v2:
        st.markdown(
            """
        <div class="content-card">
            <h4>Automated Validation Test Suite</h4>
            <ul>
                <li><strong>TEST 1-2:</strong> Carbon/Hydrogen/Oxygen mass conservation.</li>
                <li><strong>TEST 3-4:</strong> Zero permeance MR strictly reduces to conventional TR.</li>
                <li><strong>TEST 5:</strong> Large permeance enhances H2O removal within physical bounds.</li>
                <li><strong>TEST 8:</strong> Flow reduction increases residence time and conversion.</li>
                <li><strong>TEST 10:</strong> Pressure elevation increases yield (Le Chatelier).</li>
                <li><strong>TEST 11-12:</strong> Deterministic bitwise reproducibility and solver sensitivity.</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
