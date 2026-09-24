"""Offline tests for the OSPAR handler's source-loading boundary (`load_data`)."""

import pandas as pd
import pytest

from marisco.handlers.ospar import _source_path, load_data


def write_source_csvs(directory, biota_columns=None, seawater_columns=None):
    """Write the smallest representative OSPAR source pair."""
    biota_columns = biota_columns or {
        "ID": [1],
        "Sample type": ["BIOT"],
        "Species": ["Ostrea edulis"],
        "Provider extension": ["kept"],
    }
    seawater_columns = seawater_columns or {
        "ID": [2],
        "Sampling depth": [3.0],
        "Provider extension": ["kept"],
    }
    pd.DataFrame(biota_columns).to_csv(directory / "Biota data.csv", index=False)
    pd.DataFrame(seawater_columns).to_csv(directory / "Seawater data.csv", index=False)


def test_load_data_reads_biota_and_keeps_extra_provider_columns(tmp_path):
    write_source_csvs(tmp_path)

    dfs = load_data(str(tmp_path))

    assert dfs["BIOTA"].shape == (1, 4)
    assert dfs["BIOTA"].columns.tolist() == [
        "id",
        "sample type",
        "species",
        "provider extension",
    ]
    assert dfs["BIOTA"].loc[0, "provider extension"] == "kept"


def test_load_data_reads_seawater(tmp_path):
    write_source_csvs(tmp_path)

    dfs = load_data(str(tmp_path))

    assert dfs["SEAWATER"].shape == (1, 3)
    assert dfs["SEAWATER"].columns.tolist() == [
        "id",
        "sampling depth",
        "provider extension",
    ]


def test_load_data_fails_for_missing_source_file(tmp_path):
    pd.DataFrame({"ID": [1], "Species": ["Ostrea edulis"]}).to_csv(
        tmp_path / "Biota data.csv", index=False
    )

    with pytest.raises(FileNotFoundError):
        load_data(str(tmp_path))


def test_load_data_fails_for_missing_required_column(tmp_path):
    write_source_csvs(tmp_path, biota_columns={"ID": [1]})

    with pytest.raises(ValueError, match=r"BIOTA missing required columns.*species"):
        load_data(str(tmp_path))


def test_source_path_local_dir_uses_plain_filename(tmp_path):
    path = _source_path(str(tmp_path), "Biota data.csv")

    assert path == str(tmp_path / "Biota data.csv")
    assert "%20" not in path


def test_source_path_url_percent_encodes_spaces():
    path = _source_path(
        "https://raw.githubusercontent.com/org/repo/main/data", "Biota data.csv"
    )

    assert path == "https://raw.githubusercontent.com/org/repo/main/data/Biota%20data.csv"


def test_source_path_url_trailing_slash_does_not_double_up():
    path = _source_path(
        "https://raw.githubusercontent.com/org/repo/main/data/", "Biota data.csv"
    )

    assert path == "https://raw.githubusercontent.com/org/repo/main/data/Biota%20data.csv"
