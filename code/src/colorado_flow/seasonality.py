from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf

from .io import load_raw_csv, resolve_path, write_json


def run_seasonality(cfg: dict[str, Any]) -> dict[str, Any]:
    df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    q = df["discharge_m3s"].astype(float)
    results_dir = resolve_path(cfg, "results_dir")
    figures_dir = resolve_path(cfg, "figures_dir")
    tables_dir = resolve_path(cfg, "tables_dir")

    stl = STL(q, period=365, robust=True).fit()
    components = pd.DataFrame(
        {
            "date": q.index,
            "observed": q.to_numpy(),
            "trend": stl.trend.to_numpy(),
            "seasonal": stl.seasonal.to_numpy(),
            "resid": stl.resid.to_numpy(),
        }
    )
    components.to_csv(tables_dir / "stl_components.csv", index=False, float_format="%.6f")

    seasonal_strength = max(
        0.0, 1.0 - float(np.var(stl.resid) / np.var(stl.resid + stl.seasonal))
    )
    trend_strength = max(0.0, 1.0 - float(np.var(stl.resid) / np.var(stl.resid + stl.trend)))
    detrended = q.to_numpy() - stl.trend.to_numpy()
    acf_values = acf(detrended, nlags=400, fft=True, missing="drop")

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.2))
    ax = axes[0, 0]
    ax.plot(q.index, q, color="#64748B", linewidth=0.6, label="Quan trắc")
    ax.plot(q.index, stl.trend, color="#DC2626", linewidth=1.6, label="Trend STL")
    ax.set_title("A. Chuỗi quan trắc và thành phần xu hướng STL")
    ax.set_ylabel("m³/s")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    ax.plot(components["date"], components["seasonal"], color="#0F766E", linewidth=0.7)
    ax.set_title("B. Thành phần mùa vụ STL (period = 365 ngày)")
    ax.set_ylabel("m³/s")
    ax.grid(alpha=0.2)

    ax = axes[1, 0]
    lags = np.arange(len(acf_values))
    ax.axhline(0, color="#334155", linewidth=0.8)
    ax.plot(lags, acf_values, color="#1D4ED8", linewidth=1.2)
    for lag in (7, 30, 182, 365):
        if lag < len(acf_values):
            ax.axvline(lag, color="#DC2626", linestyle=":", linewidth=0.9)
            ax.text(lag, 0.92, str(lag), color="#DC2626", fontsize=7, ha="center")
    ax.set_xlim(0, 400)
    ax.set_ylim(-0.2, 1.0)
    ax.set_title("C. ACF của chuỗi đã tách xu hướng")
    ax.set_xlabel("Lag (ngày)")
    ax.set_ylabel("Tự tương quan")
    ax.grid(alpha=0.2)

    ax = axes[1, 1]
    ax.plot(components["date"], components["resid"], color="#64748B", linewidth=0.5)
    ax.axhline(0, color="#DC2626", linewidth=0.8)
    ax.set_title("D. Phần dư STL")
    ax.set_ylabel("m³/s")
    ax.grid(alpha=0.2)

    fig.suptitle("Phân rã STL và cấu trúc tự tương quan", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(figures_dir / "stl_seasonality.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / "stl_seasonality.pdf", bbox_inches="tight")
    plt.close(fig)

    seasonal = {
        "stl_period_days": 365,
        "stl_robust": True,
        "seasonal_strength": seasonal_strength,
        "trend_strength": trend_strength,
        "acf_lag_365": float(acf_values[365]) if len(acf_values) > 365 else None,
        "acf_lag_182": float(acf_values[182]) if len(acf_values) > 182 else None,
        "acf_lag_30": float(acf_values[30]) if len(acf_values) > 30 else None,
        "acf_lag_7": float(acf_values[7]) if len(acf_values) > 7 else None,
        "trend_start": float(stl.trend.iloc[0]),
        "trend_end": float(stl.trend.iloc[-1]),
        "trend_min": float(stl.trend.min()),
        "trend_max": float(stl.trend.max()),
    }
    write_json(results_dir / "seasonality_metrics.json", seasonal)
    return seasonal
