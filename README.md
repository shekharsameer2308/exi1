# E-Methanol Membrane Reactor Model

1D packed-bed and water-selective membrane-reactor simulation for e-methanol
synthesis from captured CO2 and renewable H2.

## Reaction System

```
CO2 + 3 H2  <=>  CH3OH + H2O    (methanol synthesis)
CO2 + H2    <=>  CO    + H2O    (reverse water-gas shift)
```

## Model Features

- **Kinetics**: Vanden Bussche & Froment (1996) LHHW model, J. Catal. 161, 1-10
- **Energy balance**: Non-isothermal with wall cooling
- **Pressure drop**: Ergun equation for packed beds
- **Membrane**: Water-selective with finite H2 and MeOH crossover
- **Thermodynamics**: Shomate Cp(T) from NIST, thermodynamic equilibrium constants
- **ML surrogate**: Random Forest trained on DOE simulation data

## Data Source

Slotboom, Y. et al. (2020). *"Data for: Critical assessment of steady-state
kinetic models for the synthesis of methanol over an industrial Cu/ZnO/Al2O3
catalyst."*  Mendeley Data v1.
[DOI: 10.17632/fxwg9nbz2z.1](https://doi.org/10.17632/fxwg9nbz2z.1)

## Project Structure

```
paper1/
  src/emethanol/
    reactor.py          Core 1D reactor model (VBF kinetics, Ergun, membrane)
    __init__.py
  scripts/
    01_prepare_data.py          Load and clean Slotboom dataset
    02_run_reactor_cases.py     PBR vs membrane-reactor comparison
    03_generate_doe.py          Design of Experiments (200 simulated cases)
    04_train_surrogate.py       Random Forest surrogate training
  data/
    raw/                        Published experimental CSV
    processed/                  Cleaned, split train/val datasets
  outputs/                      Simulation profiles and summaries
  requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run scripts in order:

```bash
python scripts/01_prepare_data.py       # Prepare experimental data
python scripts/02_run_reactor_cases.py   # PBR vs membrane comparison
python scripts/03_generate_doe.py        # Generate DOE dataset
python scripts/04_train_surrogate.py     # Train ML surrogate
```

## Disclaimer

This is a course-project model. The VBF kinetic parameters have NOT been
recalibrated against the Slotboom dataset. Do not claim industrial validity
until the model has been calibrated and validated against real data.
