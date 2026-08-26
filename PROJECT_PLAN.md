# Step-by-step implementation plan

## Step 1 — Obtain and inspect experimental data

Download the published CSV into `data/raw/`, run `scripts/01_prepare_data.py`, and inspect the reported temperature, pressure, flow and composition ranges. Reserve 20% of the experimental rows for validation.

**Deliverable:** a clean data file and an auditable data dictionary.

## Step 2 — Calibrate the conventional reactor

Start with `src/emethanol/reactor.py` in PBR mode. Replace the nominal constants in `_rates()` with parameters fit against the published data. Compare predicted and measured outlet CO2, CO, H2, methanol and water.

**Acceptance criterion:** report error metrics separately for the fitting and held-out validation sets.

## Step 3 — Add membrane transport

Enable `membrane_enabled=True`. Treat water permeance and H2O/H2 selectivity as literature inputs. Run matched PBR/MR cases at identical inlet conditions; quantify conversion gain, methanol selectivity, H2 loss and water removed.

**Acceptance criterion:** no conclusion is based on a membrane property that has not been sourced or varied in a sensitivity analysis.

## Step 4 — Extend multiphysics fidelity

Set `isothermal=False` only after selecting heat-transfer and heat-capacity correlations. Replace the simplified pressure and heat terms with parameters justified for the chosen geometry.

**Acceptance criterion:** maximum temperature and pressure loss are reported for every optimum.

## Step 5 — Generate design-of-experiments data

Run `scripts/03_generate_doe.py`. Its rows are simulated design cases, not experimental labels. Increase the sample count after the core model passes verification.

**Deliverable:** `outputs/membrane_doe.csv`.

## Step 6 — Train and assess the ML surrogate

Run `scripts/04_train_surrogate.py`. Use ML only as a fast approximation of the first-principles model. Report its hold-out R² and MAE before using it to rank designs. Do not present the surrogate as independent validation.

**Deliverable:** feature-importance table and ranked feasible designs.

## Step 7 — Final comparison

Compare PBR and MR on CO2 conversion, carbon selectivity to methanol, space-time yield, water removal, H2 loss, peak temperature, pressure drop, and estimated separation duty.

