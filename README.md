# E-Methanol Membrane Reactor Model ⚗️

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-numpy%20%7C%20scipy%20%7C%20pandas%20%7C%20scikit--learn-green)
![Status](https://img.shields.io/badge/status-active-success.svg)

A 1D packed-bed and water-selective membrane-reactor simulation pipeline for e-methanol synthesis from captured CO₂ and renewable H₂. This project includes first-principles physics modeling, experimental data preparation, and a machine learning surrogate.

## Reaction System

```text
CO2 + 3 H2  <=>  CH3OH + H2O    (Methanol Synthesis)
CO2 + H2    <=>  CO    + H2O    (Reverse Water-Gas Shift)
```

## Model Features

- **Kinetics**: Vanden Bussche & Froment (1996) LHHW model (J. Catal. 161, 1-10)
- **Energy Balance**: Non-isothermal with wall cooling
- **Pressure Drop**: Ergun equation for packed beds
- **Membrane Transport**: Water-selective membrane with finite H₂ and MeOH crossover
- **Thermodynamics**: Shomate Cp(T) from NIST, rigorous thermodynamic equilibrium limits
- **ML Surrogate**: Random Forest trained on simulated Design of Experiments (DOE)

## Preliminary Results: PBR vs Membrane Reactor
Initial simulations demonstrate that in-situ water removal dramatically enhances single-pass CO₂ conversion by shifting the thermodynamic equilibrium:
* **Standard Packed Bed Reactor (PBR):** ~14.5% CO₂ conversion
* **Membrane Reactor (MR):** ~65.4% CO₂ conversion (with 98% water removal)

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
│   └── 04_train_surrogate.py   # Trains ML surrogate on DOE data
├── data/
│   ├── raw/                    # Published experimental CSV
│   └── processed/              # Cleaned & train/val split datasets
├── outputs/                    # Simulation profiles & case summaries
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Setup & Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the scripts in sequential order to execute the full pipeline:

```bash
python scripts/01_prepare_data.py       # 1. Prepare experimental data
python scripts/02_run_reactor_cases.py  # 2. Simulate PBR vs Membrane
python scripts/03_generate_doe.py       # 3. Generate synthetic DOE dataset
python scripts/04_train_surrogate.py    # 4. Train AI/ML surrogate model
```

## Disclaimer

This is a chemical engineering course project model. The VBF kinetic parameters have **not** been fully recalibrated against the Slotboom dataset. Do not claim industrial validity until the model has been rigorously calibrated and validated against physical data.
