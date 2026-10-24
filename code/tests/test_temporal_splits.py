from __future__ import annotations

import pandas as pd

from colorado_flow.io import load_config, load_raw_csv, resolve_path
from colorado_flow.splits import build_split_manifest, period_origins


def test_split_counts_and_boundaries():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    manifest = build_split_manifest(df, cfg)
    splits = manifest["splits"]
    assert splits["train"]["n_origins"] == 3615
    assert splits["validation"]["n_origins"] == 725
    assert splits["test"]["n_origins"] == 724
    assert splits["refit"]["n_origins"] == 4346
    assert splits["validation"]["origin_start"] == "2019-12-31"
    assert splits["validation"]["origin_end"] == "2021-12-24"
    assert splits["test"]["origin_start"] == "2021-12-31"
    assert splits["test"]["origin_end"] == "2023-12-24"
    assert all(manifest["checks"].values())


def test_every_target_stays_inside_partition():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    horizon = int(cfg["split"]["horizon"])
    for name, start, end in (
        ("validation", cfg["split"]["validation_start"], cfg["split"]["validation_end"]),
        ("test", cfg["split"]["test_start"], cfg["split"]["test_end"]),
    ):
        origins = period_origins(df.index, start, end, horizon, int(cfg["split"]["min_history"]))
        targets_min = origins.min() + pd.Timedelta(days=1)
        targets_max = origins.max() + pd.Timedelta(days=horizon)
        assert targets_min >= pd.Timestamp(start)
        assert targets_max <= pd.Timestamp(end)
