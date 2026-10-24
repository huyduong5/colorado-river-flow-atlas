from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from colorado_flow.io import load_config, resolve_path


def test_web_manifest_and_daily_series():
    cfg = load_config()
    web_dir = resolve_path(cfg, "web_data_dir")
    manifest_path = web_dir / "manifest.json"
    if not manifest_path.exists():
        pytest.skip("Chưa chạy stage export")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["dataset_hash"] == (
        "f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660"
    )
    daily = json.loads((web_dir / "daily.json").read_text(encoding="utf-8"))
    assert len(daily) == 5113
    assert daily[0]["date"] == "2010-01-01"
    assert daily[-1]["date"] == "2023-12-31"


def test_web_metrics_match_csv():
    cfg = load_config()
    web_dir = resolve_path(cfg, "web_data_dir")
    metrics_path = web_dir / "metrics.json"
    if not metrics_path.exists():
        pytest.skip("Chưa chạy stage export")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))["overall"]
    csv = pd.read_csv(resolve_path(cfg, "tables_dir") / "metrics_overall.csv")
    csv = csv[csv["split"] == "test"].set_index("model")
    payload = {row["model"]: row for row in metrics if row["split"] == "test"}
    for model in ("naive", "lightgbm_direct"):
        assert payload[model]["mean_RMSE_7"] == pytest.approx(csv.loc[model, "mean_RMSE_7"], abs=1e-9)
