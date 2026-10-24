from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .io import fmt_date, write_json


def _ts(value: str | pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def period_origins(
    index: pd.DatetimeIndex,
    target_start: str | pd.Timestamp,
    target_end: str | pd.Timestamp,
    horizon: int = 7,
    min_history: int = 30,
) -> pd.DatetimeIndex:
    dates = pd.DatetimeIndex(index).normalize().sort_values()
    target_start = _ts(target_start)
    target_end = _ts(target_end)
    first = target_start - pd.Timedelta(days=1)
    first = max(first, dates.min() + pd.Timedelta(days=min_history))
    last = target_end - pd.Timedelta(days=horizon)
    if last < first:
        return pd.DatetimeIndex([])
    return pd.date_range(first, last, freq="D")


def build_split_manifest(df: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    split = cfg["split"]
    horizon = int(split["horizon"])
    min_history = int(split["min_history"])
    index = pd.DatetimeIndex(df.index)

    def make(name: str, target_start: str, target_end: str) -> dict[str, Any]:
        origins = period_origins(index, target_start, target_end, horizon, min_history)
        return {
            "name": name,
            "target_start": target_start,
            "target_end": target_end,
            "origin_start": fmt_date(origins[0]) if len(origins) else None,
            "origin_end": fmt_date(origins[-1]) if len(origins) else None,
            "n_origins": int(len(origins)),
            "horizon": horizon,
        }

    splits = {
        "train": make("train", split["train_start"], split["train_end"]),
        "validation": make("validation", split["validation_start"], split["validation_end"]),
        "test": make("test", split["test_start"], split["test_end"]),
        "refit": make("refit", split["train_start"], split["refit_end"]),
    }

    for name, meta in splits.items():
        origins = period_origins(index, meta["target_start"], meta["target_end"], horizon, min_history)
        if len(origins):
            meta["target_min_from_origins"] = fmt_date(origins[0] + pd.Timedelta(days=1))
            meta["target_max_from_origins"] = fmt_date(origins[-1] + pd.Timedelta(days=horizon))

    manifest = {
        "forecast_definition": "Tại gốc t, phát hành vector 7 nhãn q_(t+1)..q_(t+7).",
        "horizon": horizon,
        "min_history_days": min_history,
        "splits": splits,
        "checks": {
            "train_target_max_lte_train_end": splits["train"]["target_max_from_origins"]
            <= split["train_end"],
            "validation_targets_inside": splits["validation"]["target_min_from_origins"]
            >= split["validation_start"]
            and splits["validation"]["target_max_from_origins"] <= split["validation_end"],
            "test_targets_inside": splits["test"]["target_min_from_origins"] >= split["test_start"]
            and splits["test"]["target_max_from_origins"] <= split["test_end"],
            "no_random_shuffle": True,
        },
    }
    return manifest


def run_splits(cfg: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    manifest = build_split_manifest(df, cfg)
    results_dir = Path(cfg["_code_dir"]) / "results"
    write_json(results_dir / "split_manifest.json", manifest)
    return manifest
