from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .features import design_columns, split_masks


def _matrix(
    frame: pd.DataFrame, mask: pd.Series, horizon: int, require_target: bool = True
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray, pd.DatetimeIndex]:
    cols = design_columns(horizon)
    target_col = f"y_h{horizon}"
    subset = frame.loc[mask, cols + ([target_col] if require_target else [])].copy()
    if require_target:
        subset = subset.dropna(subset=cols + [target_col])
        y = subset[target_col].to_numpy(dtype=float)
    else:
        subset = subset.dropna(subset=cols)
        y = None
    x = subset[cols].to_numpy(dtype=np.float32)
    q = subset["q"].to_numpy(dtype=float)
    return x, y, q, pd.DatetimeIndex(subset.index)


def build_datasets(frame: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    masks = split_masks(frame, cfg)
    horizon = int(cfg["split"]["horizon"])
    out: dict[str, Any] = {"masks": masks, "horizon": horizon, "feature_columns": {}}
    for split_name in ("train", "validation", "refit", "test"):
        out[split_name] = {}
        for h in range(1, horizon + 1):
            x, y, q, dates = _matrix(frame, masks[split_name], h)
            out[split_name][h] = {"X": x, "y": y, "q": q, "origin_dates": dates}
        out["feature_columns"][split_name] = {
            str(h): design_columns(h) for h in range(1, horizon + 1)
        }
    return out


def build_inference_matrix(frame: pd.DataFrame, dates: pd.DatetimeIndex, horizon: int) -> tuple[np.ndarray, pd.DatetimeIndex]:
    cols = design_columns(horizon)
    subset = frame.loc[frame.index.isin(dates), cols].copy().dropna(subset=cols)
    return subset[cols].to_numpy(dtype=np.float32), pd.DatetimeIndex(subset.index)
