from __future__ import annotations

import re
import zipfile
from io import BytesIO

import numpy as np
import pandas as pd
import requests

from marisco.handlers.pipeline.contracts import HandlerConfig


KEEP_COLUMNS = [
    "Cruise",
    "Station",
    "sample_number",
    "Latitude_degN",
    "Longitude_degE",
    "DateTime",
    "Depth_m",
    "Temperature_degC",
    "Salinity_psu",
    "I129_at_kg",
    "unc_I129_at_kg",
]


def load_and_cleanse(cfg: HandlerConfig, grp: str = "SEAWATER") -> dict[str, pd.DataFrame]:
    """Load the BGOS-JOIS-2021 ZIP-wrapped workbook and return a boundary-cleansed frame."""
    response = requests.get(cfg.url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        xlsx_name = next(name for name in archive.namelist() if name.lower().endswith(".xlsx"))
        with archive.open(xlsx_name) as workbook:
            df = pd.read_excel(workbook, sheet_name=0)

    cols = [re.sub(r"\s*\([^)]*\)\s*", "", str(col)).strip() for col in df.columns]
    if cols[0] == "":
        cols[0] = "Cruise"
    df.columns = cols
    df = df.replace({r"^\s*$": np.nan}, regex=True)

    df["DateTime"] = pd.to_datetime(
        df["Date"].astype("string").str.strip() + "T" + df["Time"].astype("string").str.strip(),
        utc=True,
    )
    df["I129_at_kg"] = pd.to_numeric(df["I129_at_kg"], errors="raise") * 1e7
    df["unc_I129_at_kg"] = pd.to_numeric(df["unc_I129_at_kg"], errors="raise") * 1e7

    for col in ["sample_number", "Latitude_degN", "Longitude_degE", "Depth_m", "Temperature_degC", "Salinity_psu"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    for col in ["Cruise", "Station"]:
        df[col] = df[col].astype("string").str.strip().replace("", np.nan)

    return {grp: df[KEEP_COLUMNS].reset_index(drop=True)}
