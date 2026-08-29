import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

st.set_page_config(page_title="E-Methanol Reactor", layout="wide")

# Muted minimalist CSS
st.markdown("""
<style>
    h1, h2, h3 { color: #475569; font-family: sans-serif; }
    .content-card { 
        background-color: #f8fafc; border: 1px solid #e2e8f0; 
        padding: 1.5rem; border-radius: 0.5rem; color: #475569; 
    }
    .metric-value { color: #10b981; font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem; }
    .metric-label { font-size: 1rem; color: #6b7280; font-weight: 600; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_surrogate_model():
    """Load serialized ML model. Cached to prevent reloading on slider changes."""
    return joblib.load("surrogate_rf.joblib")

try:
    model = load_surrogate_model()
except Exception as e:
    st.error("Model not found. Please run scripts/03_generate_doe.py and 04_train_surrogate.py first.")
    st.stop()

st.title("E-Methanol Membrane Reactor Predictor")
st.markdown("Instantly predict non-isothermal ODE physics using an optimized Machine Learning surrogate.")

# Sidebar operational inputs
st.sidebar.header("Operational Parameters")
t_in = st.sidebar.slider("Inlet Temperature (K)", 463.15, 523.15, 493.15, step=1.0)
p_in = st.sidebar.slider("Inlet Pressure (bar)", 30.0, 70.0, 50.0, step=1.0)
ratio = st.sidebar.slider("H2:CO2 Ratio", 2.5, 4.0, 3.0, step=0.1)
flow = st.sidebar.slider("Inlet Flow (mol/s)", 0.01, 0.03, 0.015, step=0.001)

# Prediction
input_df = pd.DataFrame([[t_in, p_in, ratio, flow]], 
                        columns=["T_in_K", "P_in_bar", "h2_co2_ratio", "flow_mol_s"])

prediction = model.predict(input_df)[0]
co2_conv = prediction[0]
meoh_yield = prediction[1]

# Display Metrics
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="content-card">
        <div class="metric-label">CO2 Conversion</div>
        <div class="metric-value">{co2_conv * 100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="content-card">
        <div class="metric-label">Methanol Yield</div>
        <div class="metric-value">{meoh_yield * 100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Generate Plot Data (Sweep Temperature at current Pressure/Ratio/Flow)
st.markdown("### Temperature Sweep Analysis")
temps = np.linspace(463.15, 523.15, 50)
plot_inputs = pd.DataFrame({
    "T_in_K": temps,
    "P_in_bar": p_in,
    "h2_co2_ratio": ratio,
    "flow_mol_s": flow
})
plot_preds = model.predict(plot_inputs)
yields = plot_preds[:, 1] * 100 # Convert to percentage

fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(temps, yields, color="#10b981", linewidth=2.5)
ax.set_xlabel("Temperature (K)", color="#475569", fontweight="bold")
ax.set_ylabel("Methanol Yield (%)", color="#475569", fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(colors="#475569")
st.pyplot(fig)
