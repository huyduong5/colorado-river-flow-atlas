from __future__ import annotations

import pandas as pd

from colorado_flow.features import build_feature_frame, design_columns
from colorado_flow.io import load_config, load_raw_csv, resolve_path


def test_lags_and_target_dates_are_causal():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    frame = build_feature_frame(df, cfg)
    pd.testing.assert_series_equal(frame["lag_1"], df["discharge_m3s"].shift(1), check_names=False, check_freq=False)
    pd.testing.assert_series_equal(frame["lag_7"], df["discharge_m3s"].shift(7), check_names=False, check_freq=False)
    assert (frame["target_date_h1"] == frame.index + pd.Timedelta(days=1)).all()
    assert (frame["target_date_h7"] == frame.index + pd.Timedelta(days=7)).all()


def test_future_values_do_not_change_features_at_origin():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    changed = df.copy()
    origin = pd.Timestamp("2015-01-15")
    changed.loc[changed.index > origin, "discharge_m3s"] = 9999.0
    original = build_feature_frame(df, cfg)
    mutated = build_feature_frame(changed, cfg)
    for horizon in (1, 3, 7):
        cols = design_columns(horizon)
        pd.testing.assert_series_equal(
            original.loc[origin, cols],
            mutated.loc[origin, cols],
            check_names=False,
            check_freq=False,
        )


def test_target_calendar_is_not_missing_after_warmup():
    cfg = load_config()
    df = load_raw_csv(resolve_path(cfg, "raw_csv"))
    frame = build_feature_frame(df, cfg)
    warm = frame.loc["2010-01-31":]
    assert warm["target_doy_h1"].notna().all()
    assert warm["target_month_h7"].notna().all()
