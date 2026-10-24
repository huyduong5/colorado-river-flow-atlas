from __future__ import annotations

from typing import Any

import pandas as pd


def predict(
    df: pd.DataFrame,
    origins: pd.DatetimeIndex,
    horizon: int = 7,
    lag: int = 365,
    model_name: str = "seasonal_naive_365",
) -> pd.DataFrame:
    q = df["discharge_m3s"].astype(float)
    rows: list[dict[str, Any]] = []
    for origin in origins:
        origin = pd.Timestamp(origin).normalize()
        for h in range(1, horizon + 1):
            target = origin + pd.Timedelta(days=h)
            source = target - pd.Timedelta(days=lag)
            y_pred = float(q.loc[source]) if source in q.index else None
            y_true = float(q.loc[target]) if target in q.index else None
            rows.append(
                {
                    "model": model_name,
                    "origin_date": origin,
                    "target_date": target,
                    "horizon": h,
                    "y_true": y_true,
                    "y_pred": y_pred,
                }
            )
    return pd.DataFrame(rows)
