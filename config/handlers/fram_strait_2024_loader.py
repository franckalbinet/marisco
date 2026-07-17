from __future__ import annotations

from io import BytesIO

import pandas as pd
import requests


RAW_COLUMNS = [
    "Cruise",
    "Year",
    "Station",
    "Latitude",
    "Longitude",
    "Depth",
    "Salinity",
    "Theta_C",
    "Sigma0",
    "I129_conc_x1e7_at_kg",
    "I129_unc_x1e7_at_kg",
    "U236_conc_x1e6_at_kg",
    "U236_unc_x1e6_at_kg",
    "Water_mass",
    "Tracer_Category",
    "Ref",
]

KEEP_COLUMNS = [
    "Year",
    "Station",
    "Latitude",
    "Longitude",
    "Depth",
    "Salinity",
    "Theta_C",
    "I129_at_kg",
    "I129_unc_at_kg",
    "U236_at_kg",
    "U236_unc_at_kg",
]


def load_and_cleanse(cfg, grp: str = "SEAWATER"):
    """Load and boundary-clean the Fram Strait 2024 supplementary Excel workbook."""
    response = requests.get(cfg.url, timeout=60)
    response.raise_for_status()

    raw = pd.read_excel(BytesIO(response.content), sheet_name="Data", header=None)
    df = raw.copy()
    df.columns = [None, *RAW_COLUMNS]
    df = df.iloc[4:].reset_index(drop=True)
    df = df.drop(columns=[None, "Cruise", "Sigma0", "Water_mass", "Tracer_Category", "Ref"])

    df = df[df["Latitude"].notna()].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").ffill()
    df["Year"] = df["Year"].astype("Int64").astype(str)

    df["I129_at_kg"] = pd.to_numeric(df["I129_conc_x1e7_at_kg"], errors="raise") * 1e7
    df["I129_unc_at_kg"] = pd.to_numeric(df["I129_unc_x1e7_at_kg"], errors="raise") * 1e7
    df["U236_at_kg"] = pd.to_numeric(df["U236_conc_x1e6_at_kg"], errors="raise") * 1e6
    df["U236_unc_at_kg"] = pd.to_numeric(df["U236_unc_x1e6_at_kg"], errors="raise") * 1e6

    for col in ["Latitude", "Longitude", "Depth", "Salinity", "Theta_C"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["Station"] = df["Station"].astype(str)

    df = df[KEEP_COLUMNS].reset_index(drop=True)
    return {grp: df}


def load_probe_raw(cfg, grp: str = "SEAWATER"):
    """Load a canonical raw-probe frame so verify() can expose surviving physical NaNs at Gate 2."""
    response = requests.get(cfg.url, timeout=60)
    response.raise_for_status()

    raw = pd.read_excel(BytesIO(response.content), sheet_name="Data", header=None)
    df = raw.copy()
    df.columns = [None, *RAW_COLUMNS]
    df = df.iloc[4:].reset_index(drop=True)
    df = df.drop(columns=[None, "Cruise", "Sigma0", "Water_mass", "Tracer_Category", "Ref"])

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["TIME"] = pd.to_datetime(df["Year"], format="%Y", errors="coerce", utc=True)
    df["I129_at_kg"] = pd.to_numeric(df["I129_conc_x1e7_at_kg"], errors="coerce") * 1e7
    df["I129_unc_at_kg"] = pd.to_numeric(df["I129_unc_x1e7_at_kg"], errors="coerce") * 1e7
    df["U236_at_kg"] = pd.to_numeric(df["U236_conc_x1e6_at_kg"], errors="coerce") * 1e6
    df["U236_unc_at_kg"] = pd.to_numeric(df["U236_unc_x1e6_at_kg"], errors="coerce") * 1e6

    for col in ["Latitude", "Longitude", "Depth", "Salinity", "Theta_C"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Station"] = df["Station"].astype(str)

    frames = []
    for nuclide, val_col, unc_col in [
        ("I129", "I129_at_kg", "I129_unc_at_kg"),
        ("U236", "U236_at_kg", "U236_unc_at_kg"),
    ]:
        sub = df[["Station", "Latitude", "Longitude", "TIME", "Depth", "Salinity", "Theta_C", val_col, unc_col]].copy()
        sub["STATION"] = sub.pop("Station")
        sub["LAT"] = sub.pop("Latitude")
        sub["LON"] = sub.pop("Longitude")
        sub["SMP_DEPTH"] = sub.pop("Depth")
        sub["SAL"] = sub.pop("Salinity")
        sub["TEMP"] = sub.pop("Theta_C")
        sub["NUCLIDE"] = nuclide
        sub["VALUE"] = sub.pop(val_col)
        sub["UNC"] = sub.pop(unc_col)
        sub["UNIT"] = "at_kg"
        sub["LAB"] = "UNSET"
        frames.append(sub)

    probe = pd.concat(frames, ignore_index=True)
    return {grp: probe}
