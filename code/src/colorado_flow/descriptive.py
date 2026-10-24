from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .io import load_raw_csv, resolve_path, write_json, write_text


def _stats(series: pd.Series) -> dict[str, float]:
    return {
        "n": int(series.count()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std_sample": float(series.std(ddof=1)),
        "min": float(series.min()),
        "p05": float(series.quantile(0.05)),
        "p25": float(series.quantile(0.25)),
        "p75": float(series.quantile(0.75)),
        "p95": float(series.quantile(0.95)),
        "max": float(series.max()),
    }


def build_descriptive_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    q = df["discharge_m3s"]
    monthly = (
        df.assign(month=df.index.month)
        .groupby("month")["discharge_m3s"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std_sample=lambda s: s.std(ddof=1),
            min="min",
            p25=lambda s: s.quantile(0.25),
            p75=lambda s: s.quantile(0.75),
            max="max",
        )
        .reset_index()
    )
    yearly = (
        df.assign(year=df.index.year)
        .groupby("year")["discharge_m3s"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std_sample=lambda s: s.std(ddof=1),
            min="min",
            p95=lambda s: s.quantile(0.95),
            max="max",
        )
        .reset_index()
    )
    month_year = (
        df.assign(year=df.index.year, month=df.index.month)
        .groupby(["year", "month"])["discharge_m3s"]
        .mean()
        .unstack("month")
    )
    month_year.columns = [f"m{int(c):02d}" for c in month_year.columns]
    month_year = month_year.reset_index()
    daily = pd.DataFrame([_stats(q)]).T.reset_index()
    daily.columns = ["metric", "value"]
    return {
        "daily": daily,
        "monthly": monthly,
        "yearly": yearly,
        "monthly_by_year": month_year,
    }


def plot_trend_seasonality(
    df: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    figures_dir: Path,
) -> Path:
    q = df["discharge_m3s"]
    monthly = tables["monthly"]
    yearly = tables["yearly"]
    month_year = tables["monthly_by_year"].set_index("year")
    month_year.columns = [int(c[1:]) for c in month_year.columns]

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.6))
    ax = axes[0, 0]
    ax.plot(q.index, q, color="#64748B", linewidth=0.6, alpha=0.65, label="Lưu lượng ngày")
    ax.plot(
        q.index,
        q.rolling(30, center=True, min_periods=15).mean(),
        color="#1D4ED8",
        linewidth=1.3,
        label="Trung bình trượt 30 ngày",
    )
    ax.plot(
        q.index,
        q.rolling(365, center=True, min_periods=183).mean(),
        color="#DC2626",
        linewidth=1.8,
        label="Trung bình trượt 365 ngày",
    )
    ax.set_title("A. Chuỗi lưu lượng ngày và xu hướng dài hạn")
    ax.set_ylabel("m³/s")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    ax.plot(yearly["year"], yearly["mean"], marker="o", color="#1D4ED8", linewidth=1.5)
    ax.fill_between(
        yearly["year"],
        yearly["min"],
        yearly["max"],
        color="#DBEAFE",
        alpha=0.65,
        label="Khoảng min–max",
    )
    ax.set_title("B. Trung bình và khoảng biến thiên theo năm")
    ax.set_ylabel("m³/s")
    ax.set_xlabel("Năm")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.grid(alpha=0.2)

    ax = axes[1, 0]
    data = [q[df.index.month == m].to_numpy() for m in range(1, 13)]
    bp = ax.boxplot(data, tick_labels=[f"T{m}" for m in range(1, 13)], patch_artist=True, showmeans=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#DBEAFE")
        patch.set_edgecolor("#1D4ED8")
    for median in bp["medians"]:
        median.set_color("#DC2626")
    ax.plot(monthly["month"], monthly["mean"], color="#0F766E", marker="o", linewidth=1.3, label="Trung bình tháng")
    ax.set_title("C. Phân bố lưu lượng theo tháng (toàn chuỗi)")
    ax.set_ylabel("m³/s")
    ax.set_xlabel("Tháng")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.grid(axis="y", alpha=0.2)

    ax = axes[1, 1]
    im = ax.imshow(month_year.to_numpy(), aspect="auto", cmap="YlGnBu", interpolation="nearest")
    ax.set_xticks(range(12), [f"T{m}" for m in range(1, 13)])
    ax.set_yticks(range(len(month_year.index)), [str(y) for y in month_year.index])
    ax.set_title("D. Trung bình tháng theo từng năm")
    ax.set_xlabel("Tháng")
    ax.set_ylabel("Năm")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("m³/s")

    fig.suptitle("Xu hướng và tính mùa vụ của lưu lượng sông Colorado, 2010–2023", fontsize=13, y=1.01)
    fig.tight_layout()
    out = figures_dir / "trend_seasonality.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / "trend_seasonality.pdf", bbox_inches="tight")
    plt.close(fig)
    return out


def run_descriptive(cfg: dict[str, Any]) -> dict[str, Any]:
    df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    tables = build_descriptive_tables(df)
    tables_dir = resolve_path(cfg, "tables_dir")
    figures_dir = resolve_path(cfg, "figures_dir")
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    tables["daily"].to_csv(tables_dir / "daily_stats.csv", index=False)
    tables["monthly"].to_csv(tables_dir / "monthly_stats.csv", index=False, float_format="%.6f")
    tables["yearly"].to_csv(tables_dir / "yearly_stats.csv", index=False, float_format="%.6f")
    tables["monthly_by_year"].to_csv(
        tables_dir / "monthly_by_year.csv", index=False, float_format="%.6f"
    )
    plot_trend_seasonality(df, tables, figures_dir)

    monthly = tables["monthly"]
    yearly = tables["yearly"]
    q1 = {
        "monthly_mean_min": {
            "month": int(monthly.loc[monthly["mean"].idxmin(), "month"]),
            "value": float(monthly["mean"].min()),
        },
        "monthly_mean_max": {
            "month": int(monthly.loc[monthly["mean"].idxmax(), "month"]),
            "value": float(monthly["mean"].max()),
        },
        "yearly_mean_min": {
            "year": int(yearly.loc[yearly["mean"].idxmin(), "year"]),
            "value": float(yearly["mean"].min()),
        },
        "yearly_mean_max": {
            "year": int(yearly.loc[yearly["mean"].idxmax(), "year"]),
            "value": float(yearly["mean"].max()),
        },
        "monthly_amplitude_mean": float(monthly["mean"].max() - monthly["mean"].min()),
        "yearly_amplitude_mean": float(yearly["mean"].max() - yearly["mean"].min()),
    }
    write_json(resolve_path(cfg, "results_dir") / "q1_summary.json", q1)
    return q1
