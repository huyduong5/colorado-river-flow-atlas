from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .io import (
    fmt_date,
    load_raw_csv,
    resolve_path,
    sha256_file,
    write_json,
)


def _longest_zero_run(series: pd.Series) -> int:
    longest = 0
    current = 0
    for value in series.to_numpy():
        if np.isfinite(value) and value == 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return int(longest)


def audit_frame(df: pd.DataFrame, dataset_hash: str) -> dict[str, Any]:
    q = df["discharge_m3s"]
    dates = pd.DatetimeIndex(df.index)
    expected = pd.date_range(dates.min(), dates.max(), freq="D")
    missing = expected.difference(dates)
    duplicates = int(dates.duplicated().sum())
    nulls = int(q.isna().sum())
    finite = pd.Series(np.isfinite(q.to_numpy()), index=df.index)
    invalid = int((~finite).sum())
    negative = int((q < 0).sum())
    zero = int((q == 0).sum())
    stats = q.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "dataset_hash": dataset_hash,
        "n_records": int(len(df)),
        "date_min": fmt_date(dates.min()),
        "date_max": fmt_date(dates.max()),
        "expected_n_days": int(len(expected)),
        "missing_dates": [fmt_date(d) for d in missing],
        "n_missing_dates": int(len(missing)),
        "duplicate_dates": duplicates,
        "nulls": nulls,
        "invalid_values": invalid,
        "negative_values": negative,
        "zero_values": zero,
        "longest_zero_run": _longest_zero_run(q),
        "unique_dates": int(dates.nunique()),
        "sorted_chronologically": bool(dates.is_monotonic_increasing),
        "stats": {
            "count": int(stats["count"]),
            "mean": float(stats["mean"]),
            "std_sample": float(q.std(ddof=1)),
            "min": float(stats["min"]),
            "p05": float(stats["5%"]),
            "p25": float(stats["25%"]),
            "median": float(stats["50%"]),
            "p75": float(stats["75%"]),
            "p95": float(stats["95%"]),
            "max": float(stats["max"]),
        },
        "calendar": {
            "n_years": int(dates.year.nunique()),
            "years": sorted(int(y) for y in dates.year.unique()),
            "n_leap_days": int(((dates.month == 2) & (dates.day == 29)).sum()),
        },
    }


def make_processed_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out.index.year.astype(int)
    out["month"] = out.index.month.astype(int)
    out["day"] = out.index.day.astype(int)
    out["day_of_year"] = out.index.dayofyear.astype(int)
    out["day_of_week"] = out.index.dayofweek.astype(int)
    out["days_in_year"] = np.where(out.index.is_leap_year, 366, 365).astype(int)
    return out


def run_audit(cfg: dict[str, Any]) -> dict[str, Any]:
    raw_path = resolve_path(cfg, "raw_csv")
    out_path = resolve_path(cfg, "processed_csv")
    quality_path = resolve_path(cfg, "results_dir") / "data_quality.json"
    table_path = resolve_path(cfg, "tables_dir") / "data_quality.csv"

    df = load_raw_csv(raw_path)
    dataset_hash = sha256_file(raw_path)
    quality = audit_frame(df, dataset_hash)
    processed = make_processed_frame(df)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(out_path, index=True, float_format="%.12f")
    write_json(quality_path, quality)

    table = pd.DataFrame(
        [
            ("Số ngày quan trắc", quality["n_records"]),
            ("Phạm vi", f"{quality['date_min']} → {quality['date_max']}"),
            ("Ngày thiếu", quality["n_missing_dates"]),
            ("Ngày trùng", quality["duplicate_dates"]),
            ("Giá trị null", quality["nulls"]),
            ("Giá trị không hữu hạn", quality["invalid_values"]),
            ("Giá trị âm", quality["negative_values"]),
            ("Giá trị bằng 0", quality["zero_values"]),
            ("Chuỗi zero dài nhất", quality["longest_zero_run"]),
            ("Trung bình (m³/s)", round(quality["stats"]["mean"], 4)),
            ("Độ lệch chuẩn mẫu (m³/s)", round(quality["stats"]["std_sample"], 4)),
            ("Nhỏ nhất (m³/s)", round(quality["stats"]["min"], 4)),
            ("Q95 (m³/s)", round(quality["stats"]["p95"], 6)),
            ("Lớn nhất (m³/s)", round(quality["stats"]["max"], 4)),
            ("SHA256", quality["dataset_hash"]),
        ],
        columns=["Hạng mục", "Giá trị"],
    )
    table.to_csv(table_path, index=False, encoding="utf-8")
    return quality
