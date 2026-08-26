"""Prepare the published Slotboom et al. kinetics dataset for model validation.

Data source
-----------
Slotboom, Y. et al. (2020). "Data for: Critical assessment of steady-state
kinetic models for the synthesis of methanol over an industrial
Cu/ZnO/Al2O3 catalyst."  Mendeley Data v1.
DOI: 10.17632/fxwg9nbz2z.1   Licence: CC BY 4.0

If the raw CSV is not found, a labelled synthetic fallback is created so the
workflow remains runnable, but a warning is printed: synthetic data must NOT
be used for final validation.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RAW_CSV = ROOT / "data" / "raw" / "Data_Methanol_Kinetics.csv"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# Load or generate fallback
# -------------------------------------------------------------------------
if RAW_CSV.exists():
    df_raw = pd.read_csv(RAW_CSV)
    source = "published Slotboom et al. dataset"
    print(f"Loaded {len(df_raw)} rows from {RAW_CSV}")
    print(f"Source: {source}")
    print(f"Columns: {list(df_raw.columns)}\n")

    # --- Filter for plug-flow reactor rows (Reactor == 0) ---
    # Reactor == 0 is a tubular PFR; Reactor == 1 is a CSTR (spinning basket).
    # A 1-D PBR model cannot be validated against CSTR data.
    n_total = len(df_raw)
    n_pfr = (df_raw["Reactor"] == 0).sum()
    n_cstr = (df_raw["Reactor"] == 1).sum()
    print(f"Reactor types: PFR={n_pfr}, CSTR={n_cstr}, total={n_total}")
    print("Filtering for PFR (Reactor == 0) only.\n")

    df = df_raw[df_raw["Reactor"] == 0].copy()
    df.reset_index(drop=True, inplace=True)

    # --- Unit conversions and derived columns ---
    df["T_K"] = df["T"] + 273.15             # Celsius -> Kelvin

    # CO2 single-pass conversion (fractional)
    df["CO2_conversion"] = np.where(
        df["CO2_in"] > 0,
        (df["CO2_in"] - df["CO2_out"]) / df["CO2_in"],
        np.nan,
    )

    # Methanol carbon selectivity (moles MeOH formed / moles CO2 converted)
    co2_converted = df["CO2_in"] - df["CO2_out"]
    df["MeOH_selectivity"] = np.where(
        co2_converted > 0,
        df["MeOH_out"] / co2_converted,
        np.nan,
    )

    # Provenance tag
    df["data_source"] = "published Slotboom et al."

    # --- Save full cleaned PFR dataset ---
    clean_path = PROCESSED / "methanol_kinetics_clean.csv"
    df.to_csv(clean_path, index=False)
    print(f"Wrote {len(df)} PFR rows to {clean_path}")

    # --- Train / validation split (80/20) ---
    # Stratify by pressure bins to ensure both splits cover the pressure range
    p_bins = pd.cut(df["P"], bins=[0, 30, 50, 80], labels=["low", "mid", "high"])
    try:
        df_train, df_val = train_test_split(
            df, test_size=0.20, random_state=42, stratify=p_bins,
        )
    except ValueError:
        # Fall back to unstratified split if bins are too sparse
        df_train, df_val = train_test_split(
            df, test_size=0.20, random_state=42,
        )

    train_path = PROCESSED / "methanol_kinetics_train.csv"
    val_path = PROCESSED / "methanol_kinetics_val.csv"
    df_train.to_csv(train_path, index=False)
    df_val.to_csv(val_path, index=False)

    print(f"Training set : {len(df_train)} rows -> {train_path}")
    print(f"Validation set: {len(df_val)} rows -> {val_path}")

    # --- Summary statistics ---
    print("\n--- PFR dataset summary ---")
    print(f"  Temperature range : {df['T_K'].min():.1f} - {df['T_K'].max():.1f} K "
          f"({df['T'].min():.1f} - {df['T'].max():.1f} C)")
    print(f"  Pressure range    : {df['P'].min()} - {df['P'].max()} bar")
    print(f"  CO2 conversion    : {df['CO2_conversion'].min():.3f} - {df['CO2_conversion'].max():.3f}")
    print(f"  MeOH selectivity  : {df['MeOH_selectivity'].min():.3f} - {df['MeOH_selectivity'].max():.3f}")
    print(f"  Flow rate (phiV)  : {df['phiV'].min():.0f} - {df['phiV'].max():.0f} mL/min")

else:
    # Synthetic fallback -- kept for backward compatibility
    print("=" * 60)
    print("WARNING: Raw data file not found at:")
    print(f"  {RAW_CSV}")
    print("Creating SYNTHETIC DEMO DATA.")
    print("Do NOT use synthetic data for final validation.")
    print("Download the published dataset from:")
    print("  https://doi.org/10.17632/fxwg9nbz2z.1")
    print("=" * 60)

    rng = np.random.default_rng(42)
    n = 80
    t = rng.uniform(210, 270, n)
    p = rng.uniform(30, 70, n)
    h2 = rng.uniform(68, 78, n)
    co2 = rng.uniform(15, 25, n)
    conversion = np.clip(
        0.08 + 0.006 * (p - 30) - 0.002 * (t - 235) + rng.normal(0, 0.025, n),
        0.02, 0.75,
    )
    df = pd.DataFrame({
        "T": t, "P": p, "H2_in": h2, "CO2_in": co2,
        "CO2_conversion_demo": conversion,
        "is_synthetic_demo": True,
        "data_source": "synthetic demonstration -- replace before validation",
    })
    out = PROCESSED / "methanol_kinetics_clean.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} synthetic rows to {out}")
    source = "synthetic demonstration data -- replace before validation"

print(f"\nData preparation complete.  Source: {source}")
