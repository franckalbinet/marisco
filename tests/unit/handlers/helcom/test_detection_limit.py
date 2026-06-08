from __future__ import annotations

import pandas as pd

from marisco.callbacks import Transformer
from marisco.handlers.helcom import RemapDetectionLimitCB, coi_dl


def test_remap_detection_limit_uses_lookup_for_known_codes_and_defaults_unknowns() -> None:
    dfs = {
        "SEAWATER": pd.DataFrame({"< value_bq/m³": ["<", "=", "ND", None, "unexpected"]}),
        "BIOTA": pd.DataFrame({"< value_bq/kg": ["<"]}),
        "SEDIMENT": pd.DataFrame({"_DL": ["="]}),
    }

    tfm = Transformer(
        dfs,
        cbs=[RemapDetectionLimitCB(coi_dl, fn_lut=lambda: {"=": 1, "<": 2, "ND": 3})],
    )

    tfm()

    assert tfm.dfs["SEAWATER"]["DL"].tolist() == [2, 1, 3, 1, 1]
    assert tfm.dfs["BIOTA"]["DL"].tolist() == [2]
    assert tfm.dfs["SEDIMENT"]["DL"].tolist() == [1]
