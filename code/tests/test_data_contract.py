from __future__ import annotations

import numpy as np
import pandas as pd

from colorado_flow.io import load_config, load_raw_csv, resolve_path, sha256_file


def test_dataset_shape_and_calendar():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    assert len(df) == 5113
    assert df.index.min() == pd.Timestamp("2010-01-01")
    assert df.index.max() == pd.Timestamp("2023-12-31")
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    expected = pd.date_range("2010-01-01", "2023-12-31", freq="D")
    assert len(expected.difference(df.index)) == 0


def test_dataset_values_and_hash():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    q = df["discharge_m3s"]
    assert q.notna().all()
    assert np.isfinite(q.to_numpy()).all()
    assert (q >= 0).all()
    assert q.min() == pytest_approx(94.39091925072448)
    assert q.max() == pytest_approx(457.4859835132164)
    assert sha256_file(resolve_path(cfg, "raw_csv")) == (
        "f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660"
    )


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, abs=1e-9)


def test_q95_and_extreme_count():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    q = df["discharge_m3s"]
    threshold = float(np.quantile(q.to_numpy(), 0.95, method="linear"))
    assert threshold == pytest_approx(417.2308539676593)
    assert int((q > threshold).sum()) == 256
