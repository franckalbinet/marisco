from __future__ import annotations

from pathlib import Path

import pandas as pd

import marisco.handlers.helcom as helcom


def test_encode_uses_explicit_data_loader_instead_of_module_source_state(monkeypatch, tmp_path: Path) -> None:
    fake_dfs = {
        "SEAWATER": pd.DataFrame(),
        "BIOTA": pd.DataFrame(),
        "SEDIMENT": pd.DataFrame(),
    }
    calls: dict[str, object] = {}

    def fake_loader():
        calls["loader_called"] = True
        return fake_dfs

    class FakeTransformer:
        def __init__(self, dfs, cbs):
            calls["transformer_dfs"] = dfs
            self.dfs = dfs
            self.logs = []

        def __call__(self):
            calls["transformer_called"] = True
            return self.dfs

    class FakeEncoder:
        def __init__(self, dfs, dest_fname, global_attrs, verbose=False):
            calls["encoder_dfs"] = dfs
            calls["dest_fname"] = dest_fname
            calls["global_attrs"] = global_attrs

        def encode(self):
            calls["encoder_called"] = True

    monkeypatch.setattr(
        helcom,
        "load_data",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("load_data should not be called")),
    )
    monkeypatch.setattr(helcom, "Transformer", FakeTransformer)
    monkeypatch.setattr(helcom, "NetCDFEncoder", FakeEncoder)
    monkeypatch.setattr(helcom, "get_attrs", lambda tfm, zotero_key, kw: {"source": "fake"})

    helcom.encode(str(tmp_path / "out.nc"), data_loader=fake_loader)

    assert calls["loader_called"] is True
    assert calls["transformer_called"] is True
    assert calls["transformer_dfs"] is fake_dfs
    assert calls["encoder_dfs"] is fake_dfs
    assert calls["encoder_called"] is True
