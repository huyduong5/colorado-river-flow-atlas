from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from colorado_flow.metrics import mae, nse, rmse, summarize_metrics


def test_metric_formulas():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    perfect = y.copy()
    mean_pred = np.full_like(y, y.mean())
    assert rmse(y, perfect) == 0.0
    assert mae(y, perfect) == 0.0
    assert nse(y, perfect) == 1.0
    assert nse(y, mean_pred) == pytest.approx(0.0, abs=1e-12)
    assert rmse(y, mean_pred) == pytest.approx(np.std(y), abs=1e-12)
    assert nse(y, np.full_like(y, 100.0)) < 0


def test_nse_undefined_for_constant_truth():
    y = np.array([5.0, 5.0, 5.0])
    pred = np.array([4.0, 5.0, 6.0])
    assert np.isnan(nse(y, pred))


def test_aggregation_uses_same_rows():
    rows = []
    for h in (1, 2):
        for i in range(10):
            rows.append(
                {
                    "run_id": "r",
                    "model": "m",
                    "split": "test",
                    "origin_date": pd.Timestamp("2022-01-01") + pd.Timedelta(days=i),
                    "target_date": pd.Timestamp("2022-01-02") + pd.Timedelta(days=i),
                    "horizon": h,
                    "y_true": float(i + h),
                    "y_pred": float(i + h + 0.5),
                }
            )
    metrics = summarize_metrics(pd.DataFrame(rows))
    assert set(metrics["by_horizon"]["horizon"]) == {1, 2}
    overall = metrics["overall"].iloc[0]
    assert overall["n_pairs"] == 20
    assert overall["n_origins"] == 10
    assert overall["mean_RMSE_7"] == pytest.approx(0.5)
    assert overall["pooled_RMSE"] == pytest.approx(0.5)
