# E-Methanol Membrane Reactor Model

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-numpy%20%7C%20scipy%20%7C%20pandas%20%7C%20scikit--learn%20%7C%20streamlit-green)
![Status](https://img.shields.io/badge/status-active-success.svg)

A 1D packed-bed and water-selective membrane-reactor simulation pipeline for e-methanol synthesis from captured CO2 and renewable H2. This project includes first-principles physics modeling, experimental data preparation, a machine learning surrogate, and an interactive Streamlit dashboard.

## Reactor Modeling Data & Equations

This project uses a rigorous first-principles physics approach to model the catalytic conversion of carbon dioxide to methanol.

### 1. Reaction Kinetics (Vanden Bussche & Froment, 1996)
The model utilizes the LHHW (Langmuir-Hinshelwood-Hougen-Watson) rate expressions derived by Vanden Bussche and Froment for a Cu/ZnO/Al2O3 commercial catalyst.

*   **Methanol Synthesis (R1):** `CO2 + 3 H2 <=> CH3OH + H2O`
*   **Reverse Water-Gas Shift (R2):** `CO2 + H2 <=> CO + H2O`

The kinetic rates ($r$, in mol/kg_cat/s) are defined by:

$$ r_{CH_3OH} = \frac{k_5 K'_{H_2O} p_{CO_2} p_{H_2} \left(1 - \frac{p_{CH_3OH} p_{H_2O}}{K_{eq1} p_{CO_2} p_{H_2}^3}\right)}{\left(1 + K_{H_2O/H_2} \frac{p_{H_2O}}{p_{H_2}^{0.5}} + K_{H_2}^{0.5} p_{H_2}^{0.5} + K_{H_2O} p_{H_2O}\right)^3} $$

$$ r_{RWGS} = \frac{k_1 p_{CO_2} p_{H_2} \left(1 - \frac{p_{CO} p_{H_2O}}{K_{eq3} p_{CO_2} p_{H_2}}\right)}{1 + K_{H_2O/H_2} \frac{p_{H_2O}}{p_{H_2}^{0.5}} + K_{H_2}^{0.5} p_{H_2}^{0.5} + K_{H_2O} p_{H_2O}} $$

### 2. Mass Balance & Membrane Transport
The 1D plug flow reactor mass balance for species `i` integrates over the reactor length `z`:

$$ \frac{dF_i}{dz} = \rho_{cat} A_{cs} \sum (\nu_{ij} r_j) - \pi D_{tube} J_i $$

Where $J_i$ is the membrane flux (mol / m² / s). By using a water-selective membrane to continuously remove $H_2O$, the equilibrium of the Methanol Synthesis reaction is driven forward (Le Chatelier's Principle).

### 3. Energy Balance
Non-isothermal integration accounting for exothermic methanol synthesis and endothermic RWGS, coupled with wall cooling:

$$ \frac{dT}{dz} = \frac{\rho_{cat} A_{cs} \sum (-\Delta H_{rxn,j} r_j) - U \pi D_{tube} (T - T_{cool})}{\sum F_i C_{p,i}} $$

Heat capacities ($C_p$) are computed dynamically using the Shomate equations from the NIST Chemistry WebBook.

### 4. Pressure Drop
The Ergun equation governs the momentum balance (pressure drop) in the packed bed:

$$ \frac{dP}{dz} = - \left[ \frac{150 \mu (1-\epsilon)^2}{D_p^2 \epsilon^3} u_s + \frac{1.75 \rho_{gas} (1-\epsilon)}{D_p \epsilon^3} u_s^2 \right] $$


## Preliminary Results: PBR vs Membrane Reactor
Initial ODE simulations demonstrate that in-situ water removal dramatically enhances single-pass CO2 conversion by shifting the thermodynamic equilibrium:
* **Standard Packed Bed Reactor (PBR):** ~14.5% CO2 conversion
* **Membrane Reactor (MR):** ~65.4% CO2 conversion (with 98% water removal)

## Data Source

Slotboom, Y. et al. (2020). *"Data for: Critical assessment of steady-state kinetic models for the synthesis of methanol over an industrial Cu/ZnO/Al2O3 catalyst."* Mendeley Data v1.
[DOI: 10.17632/fxwg9nbz2z.1](https://doi.org/10.17632/fxwg9nbz2z.1)

## Project Structure

```text
exi1/
├── src/emethanol/
│   ├── reactor.py              # Core 1D reactor model (Physics, ODEs, Kinetics)
│   └── __init__.py
├── scripts/
│   ├── 01_prepare_data.py      # Cleans Slotboom dataset (filters PFR runs)
│   ├── 02_run_reactor_cases.py # Compares PBR vs Membrane Reactor
│   ├── 03_generate_doe.py      # Generates 200 randomized cases
│   ├── 04_train_surrogate.py   # Trains ML surrogate on DOE data
│   ├── 05_analytical_report.py # Generates Excel Analytics
│   └── 06_generate_heatmaps.py # Generates Axial Thermal profiles
├── data/
│   ├── raw/                    # Published experimental CSV
│   └── processed/              # Cleaned & train/val split datasets
├── outputs/                    # Simulation profiles & case summaries
├── notebooks/
│   └── 01_Surrogate_Predictor.ipynb # Jupyter notebook ML predictor
├── app.py                      # Interactive Streamlit Dashboard
└── README.md                   # Project documentation
```

## Setup & Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install streamlit
```

## Running the Interactive Dashboard
A minimalist Streamlit dashboard has been built using the project's styling guidelines. It runs the Random Forest surrogate model to give instant predictions of the reactor performance without needing to wait for the ODE solver.

```bash
streamlit run app.py
```

## Disclaimer
This is a chemical engineering course project model. The VBF kinetic parameters have **not** been fully recalibrated against the Slotboom dataset. Do not claim industrial validity until the model has been rigorously calibrated and validated against physical data.
