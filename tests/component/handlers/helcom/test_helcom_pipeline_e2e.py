from __future__ import annotations

import socket

import pandas as pd
import pytest
import requests

from marisco.callbacks import Transformer, LowerStripNameCB, SanitizeLonLatCB, EncodeTimeCB
from marisco.handlers.helcom import (
    AddDepthCB,
    AddSalinityCB,
    AddSampleIDCB,
    AddStationCB,
    AddTemperatureCB,
    NormalizeCoordinatesCB,
    NormalizeUncCB,
    ParseCoordinates,
    ParseTimeCB,
    RemapDetectionLimitCB,
    RemapNuclideNameCB,
    RemapUnitCB,
    SanitizeValueCB,
    _normalize_coordinate_columns,
    _normalize_coordinate_rows,
    coi_dl,
    coi_val,
)
from marisco.utils import Match, ddmm_to_dd


@pytest.fixture(autouse=True)
def forbid_network_calls(monkeypatch):
    def _blocked(*args, **kwargs):
        raise RuntimeError("Network calls strictly forbidden during test!")

    monkeypatch.setattr(requests, "get", _blocked)
    monkeypatch.setattr(requests.sessions.Session, "request", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def test_helcom_logging_and_callback_flow_pure_in_memory():
    """Run the HELCOM callback chain in memory and verify native logging output."""

    df = pd.DataFrame(
        {
            "key": [1001, 1002],
            "station": ["ST-01", "ST-02"],
            "date": ["06/08/26 12:00:00", None],
            "year": [2026, 2026],
            "month": [6, 0],
            "day": [8, 1],
            "nuclide": ["CS137", "CS137"],
            "value_bq/m³": [15.4, 0.05],
            "error%_m³": [5.0, 10.0],
            "< value_bq/m³": ["=", "<"],
            "salin": [38.1, 38.2],
            "ttemp": [18.5, 18.6],
            "sdepth": [5.0, 6.0],
            "latitud (dddddd)": [43.7311, 0.0],
            "longitud (dddddd)": [7.4201, 0.0],
            "latitud (ddmmmm)": [4373.11, None],
            "longitud (ddmmmm)": [742.01, None],
        }
    )

    def fake_lut_nuclides(_df):
        return {"cs137": Match(33, "cs137", "cs137", 100)}

    dfs = {"SEAWATER": df}
    tfm = Transformer(
        dfs,
        cbs=[
            LowerStripNameCB(col_src="nuclide", col_dst="NUCLIDE"),
            RemapNuclideNameCB(fake_lut_nuclides, col_name="NUCLIDE"),
            ParseTimeCB(),
            EncodeTimeCB(),
            SanitizeValueCB(coi_val),
            NormalizeUncCB(),
            RemapUnitCB(),
            RemapDetectionLimitCB(coi_dl),
            AddSampleIDCB(),
            AddDepthCB(),
            AddSalinityCB(),
            AddTemperatureCB(),
            NormalizeCoordinatesCB(_normalize_coordinate_columns, _normalize_coordinate_rows),
            ParseCoordinates(ddmm_to_dd),
            SanitizeLonLatCB(),
            AddStationCB(),
        ],
    )
    tfm()

    publisher_postprocess_logs = ", ".join(tfm.logs)
    print(f"\n--- In-Memory HELCOM Logs ---\n{publisher_postprocess_logs}\n-----------------------------")

    assert any("Remap detection limit columns into MARIS-standard flags" in log for log in tfm.logs)
    assert any("Populate the MARIS SAL column" in log for log in tfm.logs)
    assert any("Populate the MARIS TEMP column" in log for log in tfm.logs)
    assert any("NormalizeCoordinatesCB[SEAWATER]" in log for log in tfm.logs)
    assert any("ParseTimeCB[SEAWATER]" in log for log in tfm.logs)
    assert any("ParseCoordinates[SEAWATER]" in log for log in tfm.logs)

    assert "Remap detection limit columns into MARIS-standard flags" in publisher_postprocess_logs
    assert "NormalizeCoordinatesCB[SEAWATER]" in publisher_postprocess_logs
    assert "ParseTimeCB[SEAWATER]" in publisher_postprocess_logs
