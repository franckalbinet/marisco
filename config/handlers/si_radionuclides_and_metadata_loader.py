from __future__ import annotations

from io import BytesIO

import numpy as np
import pandas as pd
import requests

from marisco.handlers.pipeline.contracts import HandlerConfig


KEEP_COLUMNS = [
    "Station",
    "Latitude_degN",
    "Longitude_degE",
    "Date",
    "Sample_ID",
    "Pressure_dbar",
    "Temperature_degC",
    "Salinity_psu",
    "I129_at_kg",
    "unc_I129_at_kg",
    "U236_at_kg",
    "unc_U236_at_kg",
]

NUMERIC_COLUMNS = [
    "Latitude_degN",
    "Longitude_degE",
    "Sample_ID",
    "Pressure_dbar",
    "Temperature_degC",
    "Salinity_psu",
    "I129_at_kg",
    "unc_I129_at_kg",
    "U236_at_kg",
    "unc_U236_at_kg",
]


def load_and_cleanse(cfg: HandlerConfig, grp: str = "SEAWATER") -> dict[str, pd.DataFrame]:
    """Load the CERN workbook and return a physically cleansed raw-schema frame."""
    response = requests.get(cfg.url, timeout=60)
    response.raise_for_status()

    df = pd.read_excel(BytesIO(response.content), sheet_name="NucData")
    df = df.replace({r"^\s*$": np.nan}, regex=True)
    df = df[KEEP_COLUMNS].copy()

    df["Date"] = (
        df["Date"]
        .astype("string")
        .str.strip()
        .str.strip('"')
        .str.strip()
    )
    df["Date"] = df["Date"].replace("", np.nan)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", utc=True)

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="raise")

    df["Station"] = df["Station"].astype("string").str.strip()
    df["Station"] = df["Station"].replace("", np.nan)

    return {grp: df.reset_index(drop=True)}
