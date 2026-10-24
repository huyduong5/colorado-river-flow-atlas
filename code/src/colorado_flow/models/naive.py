from __future__ import annotations

from typing import Any

import pandas as pd


def predict(
    df: pd.DataFrame,
    origins: pd.DatetimeIndex,
    horizon: int = 7,
    model_name: str = "naive",
) -> pd.DataFrame:
    q = df["discharge_m3s"].astype(float)
    rows: list[dict[str, Any]] = []
    for origin in origins:
        origin = pd.Timestamp(origin).normalize()
        if origin not in q.index:
            continue
        base = float(q.loc[origin])
        for h in range(1, horizon + 1):
            target = origin + pd.Timedelta(days=h)
            y_true = float(q.loc[target]) if target in q.index else None
            rows.append(
                {
                    "model": model_name,
                    "origin_date": origin,
                    "target_date": target,
                    "horizon": h,
                    "y_true": y_true,
                    "y_pred": base,
                }
            )
    return pd.DataFrame(rows)
