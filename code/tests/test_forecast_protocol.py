from __future__ import annotations

import pandas as pd

from colorado_flow.io import load_config, load_raw_csv, resolve_path
from colorado_flow.models import naive, seasonal_naive
from colorado_flow.splits import period_origins


def test_naive_and_seasonal_cover_all_horizons():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    origins = period_origins(
        df.index,
        cfg["split"]["test_start"],
        cfg["split"]["test_end"],
        int(cfg["split"]["horizon"]),
        int(cfg["split"]["min_history"]),
    )
    for predictor in (naive.predict, seasonal_naive.predict):
        pred = predictor(df, origins)
        assert len(pred) == 724 * 7
        assert set(pred["horizon"]) == set(range(1, 8))
        assert pred["y_true"].notna().all()
        assert pred["y_pred"].notna().all()
        assert (pred["target_date"] - pred["origin_date"]).dt.days.eq(pred["horizon"]).all()
        assert pred.groupby("origin_date").size().eq(7).all()
