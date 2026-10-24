from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_pred - y_true) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_pred - y_true)))


def nse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denominator = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if denominator == 0.0 or not np.isfinite(denominator):
        return float("nan")
    return float(1.0 - np.sum((y_pred - y_true) ** 2) / denominator)


def metric_row(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {"n": int(len(y_true)), "RMSE": rmse(y_true, y_pred), "MAE": mae(y_true, y_pred), "NSE": nse(y_true, y_pred)}


def metrics_by_horizon(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (run_id, model, split, horizon), group in predictions.groupby(
        ["run_id", "model", "split", "horizon"], sort=True
    ):
        row = {
            "run_id": run_id,
            "model": model,
            "split": split,
            "horizon": int(horizon),
        }
        row.update(metric_row(group["y_true"].to_numpy(), group["y_pred"].to_numpy()))
        rows.append(row)
    return pd.DataFrame(rows)


def metrics_overall(predictions: pd.DataFrame, by_horizon: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (run_id, model, split), group in predictions.groupby(["run_id", "model", "split"], sort=True):
        horizon_rows = by_horizon[
            (by_horizon["run_id"] == run_id)
            & (by_horizon["model"] == model)
            & (by_horizon["split"] == split)
        ]
        pooled = metric_row(group["y_true"].to_numpy(), group["y_pred"].to_numpy())
        rows.append(
            {
                "run_id": run_id,
                "model": model,
                "split": split,
                "n_origins": int(group["origin_date"].nunique()),
                "n_pairs": int(len(group)),
                "mean_RMSE_7": float(horizon_rows["RMSE"].mean()),
                "mean_MAE_7": float(horizon_rows["MAE"].mean()),
                "mean_NSE_7": float(horizon_rows["NSE"].mean()),
                "pooled_RMSE": pooled["RMSE"],
                "pooled_MAE": pooled["MAE"],
                "pooled_NSE": pooled["NSE"],
            }
        )
    return pd.DataFrame(rows)


def metrics_by_year(predictions: pd.DataFrame) -> pd.DataFrame:
    data = predictions.copy()
    data["target_year"] = pd.to_datetime(data["target_date"]).dt.year.astype(int)
    rows: list[dict[str, Any]] = []
    for (run_id, model, split, year, horizon), group in data.groupby(
        ["run_id", "model", "split", "target_year", "horizon"], sort=True
    ):
        row = {
            "run_id": run_id,
            "model": model,
            "split": split,
            "target_year": int(year),
            "horizon": int(horizon),
        }
        row.update(metric_row(group["y_true"].to_numpy(), group["y_pred"].to_numpy()))
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_metrics(predictions: pd.DataFrame) -> dict[str, pd.DataFrame]:
    by_horizon = metrics_by_horizon(predictions)
    overall = metrics_overall(predictions, by_horizon)
    by_year = metrics_by_year(predictions)
    return {"by_horizon": by_horizon, "overall": overall, "by_year": by_year}
