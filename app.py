import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import os

# Enforce minimalist design rules from AGENTS.md
st.set_page_config(page_title="Membrane Reactor Dashboard", layout="wide")

st.markdown("""
<style>
    /* Muted Color Scheme & Minimalist Aesthetics */
    h1, h2, h3, h4 { color: #475569; font-family: sans-serif; font-weight: 600; }
    .content-card { 
        background-color: #f8fafc; 
        border: 1px solid #e2e8f0; 
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        color: #475569; 
    }
    .neutral-badge { 
        background-color: #e2e8f0; 
        color: #475569; 
        padding: 0.25rem 0.5rem; 
        border-radius: 0.25rem; 
        font-size: 0.875em; 
        font-weight: 500;
        border: 1px solid #cbd5e1;
    }
    .metric-value { color: #10b981; font-size: 2.2rem; font-weight: bold; margin-top: 0.5rem; }
    
    /* Hide emojis in standard st.info/st.warning if possible, maintaining clean look */
    .stAlert { color: #475569; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_and_train_models():
    # Load the DOE dataset
    csv_path = "outputs/membrane_doe.csv"
    if not os.path.exists(csv_path):
        st.error(f"Dataset not found at {csv_path}. Please run scripts/03_generate_doe.py first.")
        return None
        
    df = pd.read_csv(csv_path)
    features = ['inlet_temperature_k', 'inlet_pressure_bar', 'inlet_flow_mol_s', 'h2_co2_ratio', 'length_m', 'water_permeance_mol_m2_s_pa', 'sweep_water_partial_pressure_bar']
    targets = ['co2_conversion', 'methanol_selectivity_carbon', 'methanol_sty_kg_m3cat_h']
    
    X = df[features]
    models = {}
    for target in targets:
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, df[target])
        models[target] = rf
    return models

models = load_and_train_models()

st.title("E-Methanol Reactor Predictive Dashboard")
st.markdown("Real-time surrogate model predictions for membrane reactor performance.")

# Sidebar Configuration
st.sidebar.header("Operating Conditions")
t_in = st.sidebar.slider("Inlet Temperature (K)", 463.15, 533.15, 493.15)
p_in = st.sidebar.slider("Inlet Pressure (bar)", 20.0, 70.0, 50.0)
flow = st.sidebar.slider("Inlet Flow (mol/s)", 0.008, 0.030, 0.015)
ratio = st.sidebar.slider("H2:CO2 Ratio", 3.0, 4.0, 3.2)
length = st.sidebar.slider("Reactor Length (m)", 0.5, 2.0, 1.0)
permeance = st.sidebar.number_input("Water Permeance", value=1e-7, format="%.2e")
sweep_p = st.sidebar.number_input("Sweep Pressure (bar)", value=1e-4, format="%.2e")

if models:
    # Prepare input for prediction
    input_data = pd.DataFrame([{
        'inlet_temperature_k': t_in,
        'inlet_pressure_bar': p_in,
        'inlet_flow_mol_s': flow,
        'h2_co2_ratio': ratio,
        'length_m': length,
        'water_permeance_mol_m2_s_pa': permeance,
        'sweep_water_partial_pressure_bar': sweep_p
    }])

    # Predict
    pred_conv = models['co2_conversion'].predict(input_data)[0]
    pred_sel = models['methanol_selectivity_carbon'].predict(input_data)[0]
    pred_sty = models['methanol_sty_kg_m3cat_h'].predict(input_data)[0]

    # Display Metrics in strict styled cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="content-card">
            <h4>CO2 Conversion</h4>
            <div class="metric-value">{pred_conv * 100:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="content-card">
            <h4>Methanol Selectivity</h4>
            <div class="metric-value">{pred_sel * 100:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="content-card">
            <h4>Space-Time Yield</h4>
            <div class="metric-value">{pred_sty:.5f} <span style="font-size: 0.5em; color: #6b7280; font-weight: normal;">kg/m³/h</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    ### Reactor Information
    <div class="content-card">
        <span class="neutral-badge">Kinetics</span> Vanden Bussche & Froment (1996)<br><br>
        <span class="neutral-badge">Model</span> 1D Non-isothermal Plug Flow<br><br>
        <span class="neutral-badge">Surrogate</span> Random Forest Regressor (Trained on 200 ODE simulations)
    </div>
    """, unsafe_allow_html=True)
