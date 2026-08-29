# E-Methanol Membrane Reactor

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B)
![SciML](https://img.shields.io/badge/SciML-Enabled-brightgreen)
![License](https://img.shields.io/badge/License-MIT-gray)

## Overview
E-Methanol Membrane Reactors represent a critical frontier in green energy, utilizing captured CO₂ and renewable hydrogen to synthesize clean liquid fuels. Traditional methanol synthesis is severely limited by thermodynamic equilibrium. By introducing a water-selective membrane into the reactor core, we continuously remove the H₂O byproduct, dynamically shifting the chemical equilibrium forward (via Le Chatelier's Principle) to dramatically increase single-pass CO₂ conversion and methanol yield.

Simulating these complex, non-isothermal reaction profiles traditionally requires solving highly stiff ordinary differential equations (ODEs), which is computationally expensive and slow to optimize. This project bridges first-principles chemical engineering with Scientific Machine Learning (SciML) to eliminate that computational bottleneck.

We built a deterministic 1D Plug Flow Membrane Reactor physics engine to generate high-fidelity synthetic operational data. That physics data is then used to train a multi-output Machine Learning surrogate model. The result is a blazingly fast, highly accurate Streamlit dashboard that allows researchers and engineers to instantly predict reactor performance across varying temperatures, pressures, and flow rates without waiting for iterative numerical solvers.

## Core Features
* **Rigorous Physics Engine**: A robust 1D non-isothermal Plug Flow Reactor (PFR) model solving stiff mass and energy balances using `scipy.integrate.solve_ivp`.
* **VBF Kinetics**: Implements the industry-standard Vanden Bussche & Froment (1996) LHHW kinetic rate expressions for CO₂ hydrogenation.
* **SciML Surrogate Model**: Replaces computationally heavy ODEs with a highly optimized, serialized Multi-Output Random Forest Regressor for sub-millisecond inference.
* **Interactive Dashboard**: A minimalist, production-ready Streamlit UI providing instant predictive insights and temperature sweep analytics.

## Project Architecture
```text
exi1/
├── src/emethanol/
│   ├── reactor.py                # Core ODE solver, VBF kinetics, & mass/energy balances
│   └── __init__.py               # Python package initialization
├── scripts/
│   ├── 03_generate_doe.py        # Solves ODEs to generate synthetic Design of Experiments (DOE)
│   └── 04_train_surrogate.py     # Trains & serializes the Multi-Output ML surrogate model
├── app.py                        # Streamlit dashboard for real-time inference
├── requirements.txt              # Strict dependencies for Streamlit Community Cloud deployment
└── surrogate_rf.joblib           # Pre-trained serialized Machine Learning model
```

## Quickstart & Installation
This project relies on `uv` for lightning-fast virtual environment creation and dependency resolution.

```bash
# 1. Clone the repository
git clone https://github.com/shekharsameer2308/exi1.git
cd exi1

# 2. Create a virtual environment and install dependencies using uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

## Execution Pipeline
To regenerate the data and retrain the Machine Learning models from scratch, execute the pipeline scripts in order:

```bash
# Step 1: Generate synthetic operational data (200 rows) by solving the physics ODEs
python scripts/03_generate_doe.py

# Step 2: Train the ML surrogate model on the generated data and serialize it
python scripts/04_train_surrogate.py

# Step 3: Serve the updated model via the dashboard
streamlit run app.py
```

## Mathematical Context
The core physics engine (`src/emethanol/reactor.py`) calculates species flow rates and temperature gradients along the reactor axis by evaluating differential equations. 

* **Kinetics**: Relies on the established Vanden Bussche and Froment (VBF) kinetic network, accounting for competitive adsorption of H₂O and CO₂.
* **Mass Balance**: Evaluates stoichiometric consumption coupled with a Linear Driving Force (LDF) model for selective H₂O membrane permeation.
* **Safety & Determinism**: The solver features explicit error handling for matrix non-convergence and enforces strict physical boundaries on pressures and flow rates to guarantee deterministic outputs.
