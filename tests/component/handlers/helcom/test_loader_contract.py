from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from marisco.handlers import helcom


RAW_FIXTURE_DIR = Path(__file__).resolve().parents[3] / "golden_data" / "helcom" / "raw"
CANONICAL_COORD_COLS = ["lat_ddmmmm", "lat_dddddd", "lon_ddmmmm", "lon_dddddd"]
REQUIRED_COLUMNS = {
    "SEAWATER": {
        "key",
        "nuclide",
        "date",
        "year",
        "month",
        "day",
        "value_bq/m³",
        "error%_m³",
        "< value_bq/m³",
        "station",
        *CANONICAL_COORD_COLS,
    },
    "BIOTA": {
        "key",
        "nuclide",
        "date",
        "year",
        "month",
        "day",
        "value_bq/kg",
        "error%",
        "< value_bq/kg",
        "rubin",
        "tissue",
        "basis",
        "weight",
        "station",
        *CANONICAL_COORD_COLS,
    },
    "SEDIMENT": {
        "key",
        "nuclide",
        "date",
        "year",
        "month",
        "day",
        "value_bq/kg",
        "error%_kg",
        "< value_bq/kg",
        "value_bq/m²",
        "error%_m²",
        "< value_bq/m²",
        "sedi",
        "uppsli",
        "lowsli",
        "station",
        *CANONICAL_COORD_COLS,
    },
}


def test_load_data_returns_lowercase_groups_and_canonical_coordinate_columns() -> None:
    dfs = helcom.load_data(str(RAW_FIXTURE_DIR))

    assert set(dfs) == {"BIOTA", "SEAWATER", "SEDIMENT"}

    for group_name, df in dfs.items():
        assert not df.empty
        assert all(col == col.lower() for col in df.columns)
        assert REQUIRED_COLUMNS[group_name].issubset(set(df.columns))
        _assert_coordinate_rows_are_contract_compliant(df)


def test_load_data_fails_fast_on_coordinate_contract_violations(tmp_path: Path) -> None:
    _write_csv(
        tmp_path / "SEA01.csv",
        pd.DataFrame(
            {
                "KEY": ["sea-1"],
                "DATE": ["01/01/24 00:00:00"],
                "YEAR": [2024],
                "MONTH": [1],
                "DAY": [1],
                "STATION": ["A"],
                "LATITUDE (dddddd)": [54.1],
                "LONGITUDE (dddddd)": [pd.NA],
            }
        ),
    )
    _write_csv(
        tmp_path / "SEA02.csv",
        pd.DataFrame(
            {
                "KEY": ["sea-1"],
                "NUCLIDE": ["cs137"],
                "value_bq/m³": [1.0],
                "error%_m³": [5.0],
                "< value_bq/m³": ["="],
            }
        ),
    )

    with pytest.raises(ValueError, match="invalid coordinate rows"):
        helcom.load_data(str(tmp_path), smp_types={"SEA": "SEAWATER"})


def _assert_coordinate_rows_are_contract_compliant(df: pd.DataFrame) -> None:
    decimal_complete = df["lat_dddddd"].notna() & df["lon_dddddd"].notna()
    minute_complete = df["lat_ddmmmm"].notna() & df["lon_ddmmmm"].notna()
    fully_missing = df[CANONICAL_COORD_COLS].isna().all(axis=1)

    assert not (df["lat_dddddd"].notna() ^ df["lon_dddddd"].notna()).any()
    assert not (df["lat_ddmmmm"].notna() ^ df["lon_ddmmmm"].notna()).any()
    assert not (decimal_complete & minute_complete).any()
    assert (decimal_complete | minute_complete | fully_missing).all()


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)