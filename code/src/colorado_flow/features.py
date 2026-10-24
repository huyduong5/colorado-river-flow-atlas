from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .io import resolve_path, write_json


def _calendar_columns(index: pd.DatetimeIndex, prefix: str) -> pd.DataFrame:
    days_in_year = np.where(index.is_leap_year, 366, 365).astype(float)
    doy = index.day_of_year.to_numpy(dtype=float)
    month = index.month.to_numpy(dtype=float)
    return pd.DataFrame(
        {
            f"{prefix}_doy": doy,
            f"{prefix}_doy_sin": np.sin(2 * np.pi * doy / days_in_year),
            f"{prefix}_doy_cos": np.cos(2 * np.pi * doy / days_in_year),
            f"{prefix}_month": month,
            f"{prefix}_month_sin": np.sin(2 * np.pi * (month - 1) / 12.0),
            f"{prefix}_month_cos": np.cos(2 * np.pi * (month - 1) / 12.0),
        },
        index=index,
    )


def base_feature_columns() -> list[str]:
    return [
        "q",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_21",
        "lag_28",
        "lag_30",
        "roll_mean_7",
        "roll_std_7",
        "roll_min_7",
        "roll_max_7",
        "roll_mean_14",
        "roll_std_14",
        "roll_min_14",
        "roll_max_14",
        "roll_mean_30",
        "roll_std_30",
        "roll_min_30",
        "roll_max_30",
        "diff_1",
        "diff_7",
        "origin_doy",
        "origin_doy_sin",
        "origin_doy_cos",
        "origin_month",
        "origin_month_sin",
        "origin_month_cos",
    ]


def target_calendar_columns(horizon: int) -> list[str]:
    return [
        f"target_doy_h{horizon}",
        f"target_doy_sin_h{horizon}",
        f"target_doy_cos_h{horizon}",
        f"target_month_h{horizon}",
        f"target_month_sin_h{horizon}",
        f"target_month_cos_h{horizon}",
    ]


def design_columns(horizon: int) -> list[str]:
    return base_feature_columns() + target_calendar_columns(horizon)


def build_feature_frame(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    q = df["discharge_m3s"].astype(float).copy()
    q.index = pd.DatetimeIndex(q.index).normalize()
    out = pd.DataFrame({"q": q}, index=q.index)
    for lag in cfg["features"]["lags"]:
        out[f"lag_{int(lag)}"] = q.shift(int(lag))
    for window in cfg["features"]["rolling_windows"]:
        w = int(window)
        roll = q.rolling(w, min_periods=w)
        out[f"roll_mean_{w}"] = roll.mean()
        out[f"roll_std_{w}"] = roll.std(ddof=1)
        out[f"roll_min_{w}"] = roll.min()
        out[f"roll_max_{w}"] = roll.max()
    out["diff_1"] = q - q.shift(1)
    out["diff_7"] = q - q.shift(7)
    out = out.join(_calendar_columns(out.index, "origin"))

    for h in range(1, int(cfg["split"]["horizon"]) + 1):
        target_dates = out.index + pd.Timedelta(days=h)
        cal = _calendar_columns(target_dates, "target")
        cal.index = out.index
        cal = cal.rename(columns={c: f"{c}_h{h}" for c in cal.columns})
        out = out.join(cal)
        out[f"y_h{h}"] = q.shift(-h)
        out[f"target_date_h{h}"] = target_dates
    return out


def run_features(cfg: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    frame = build_feature_frame(df, cfg)
    out_path = resolve_path(cfg, "features_csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_path, index=True, float_format="%.10f")
    write_json(
        resolve_path(cfg, "results_dir") / "feature_schema.json",
        {
            "base_columns": base_feature_columns(),
            "target_calendar_by_horizon": {
                str(h): target_calendar_columns(h) for h in range(1, int(cfg["split"]["horizon"]) + 1)
            },
            "n_rows": int(len(frame)),
            "first_complete_row": frame.dropna(subset=base_feature_columns()).index.min().strftime("%Y-%m-%d"),
        },
    )
    return frame


def load_feature_frame(cfg: dict[str, Any]) -> pd.DataFrame:
    path = resolve_path(cfg, "features_csv")
    frame = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    frame.index = pd.DatetimeIndex(frame.index)
    return frame


def split_masks(frame: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, pd.Series]:
    idx = pd.DatetimeIndex(frame.index)
    split = cfg["split"]
    horizon = int(split["horizon"])
    masks = {
        "train": (idx >= pd.Timestamp(split["train_start"]))
        & (idx + pd.Timedelta(days=horizon) <= pd.Timestamp(split["train_end"])),
        "validation": (idx >= pd.Timestamp(split["validation_start"]) - pd.Timedelta(days=1))
        & (idx + pd.Timedelta(days=horizon) <= pd.Timestamp(split["validation_end"])),
        "test": (idx >= pd.Timestamp(split["test_start"]) - pd.Timedelta(days=1))
        & (idx + pd.Timedelta(days=horizon) <= pd.Timestamp(split["test_end"])),
        "refit": (idx >= pd.Timestamp(split["train_start"]))
        & (idx + pd.Timedelta(days=horizon) <= pd.Timestamp(split["refit_end"])),
    }
    for name, mask in masks.items():
        if not mask.any():
            raise ValueError(f"Split rỗng: {name}")
    return {k: pd.Series(v, index=frame.index) for k, v in masks.items()}
