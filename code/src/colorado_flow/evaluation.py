from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .features import split_masks
from .io import load_raw_csv, resolve_path, write_json, write_text
from .metrics import summarize_metrics
from .models import lightgbm_direct, naive, seasonal_naive


MODEL_LABELS = {
    "naive": "Naive persistence",
    "seasonal_naive_365": "Seasonal Naive 365",
    "lightgbm_direct": "LightGBM direct 7 (delta)",
}


def _origins(frame: pd.DataFrame, cfg: dict[str, Any], split_name: str) -> pd.DatetimeIndex:
    masks = split_masks(frame, cfg)
    return pd.DatetimeIndex(frame.index[masks[split_name]]).sort_values()


def _attach(pred: pd.DataFrame, run_id: str, split: str) -> pd.DataFrame:
    out = pred.copy()
    out.insert(0, "run_id", run_id)
    out["split"] = split
    out["model"] = out["model"].astype(str)
    return out


def _plot_metrics(metrics: pd.DataFrame, figures_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.8))
    for ax, metric_name in zip(axes, ("RMSE", "MAE", "NSE")):
        for model, group in metrics.groupby("model"):
            group = group.sort_values("horizon")
            ax.plot(group["horizon"], group[metric_name], marker="o", linewidth=1.4, label=MODEL_LABELS.get(model, model))
        ax.set_title(metric_name)
        ax.set_xlabel("Horizon (ngày)")
        ax.set_xticks(range(1, 8))
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("m³/s")
    axes[2].set_ylabel("NSE")
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Chỉ số dự báo theo horizon trên Test 2022–2023", fontsize=12)
    fig.tight_layout()
    fig.savefig(figures_dir / "metrics_by_horizon.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / "metrics_by_horizon.pdf", bbox_inches="tight")
    plt.close(fig)


def _plot_hydrograph(predictions: pd.DataFrame, figures_dir: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(13.2, 7.2), sharex=True)
    for ax, h in zip(axes, (1, 7)):
        subset = predictions[predictions["horizon"] == h]
        for model, group in subset.groupby("model"):
            group = group.sort_values("target_date")
            ax.plot(
                group["target_date"],
                group["y_pred"],
                linewidth=1.0,
                alpha=0.85,
                label=MODEL_LABELS.get(model, model),
            )
        observed = subset[subset["model"] == "naive"].sort_values("target_date")
        ax.plot(observed["target_date"], observed["y_true"], color="#0F172A", linewidth=0.8, alpha=0.5, label="Quan trắc")
        ax.set_title(f"D+{h}")
        ax.set_ylabel("m³/s")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=7, ncol=4)
    axes[-1].set_xlabel("Ngày mục tiêu")
    fig.suptitle("So sánh dự báo rolling-origin trên Test 2022–2023", fontsize=12)
    fig.tight_layout()
    fig.savefig(figures_dir / "forecast_hydrograph.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / "forecast_hydrograph.pdf", bbox_inches="tight")
    plt.close(fig)


def _plot_scatter(predictions: pd.DataFrame, figures_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.4))
    for col, h in enumerate((1, 7)):
        subset = predictions[(predictions["model"] == "lightgbm_direct") & (predictions["horizon"] == h)]
        ax = axes[0, col]
        ax.scatter(subset["y_true"], subset["y_pred"], s=7, alpha=0.45, color="#1D4ED8")
        lim = [0, max(float(subset["y_true"].max()), float(subset["y_pred"].max())) * 1.05]
        ax.plot(lim, lim, color="#DC2626", linestyle="--", linewidth=1)
        ax.set_title(f"LightGBM D+{h}: quan trắc và dự báo")
        ax.set_xlabel("Quan trắc (m³/s)")
        ax.set_ylabel("Dự báo (m³/s)")
        ax.grid(alpha=0.2)
        ax = axes[1, col]
        ax.scatter(subset["y_pred"], subset["y_pred"] - subset["y_true"], s=7, alpha=0.45, color="#0F766E")
        ax.axhline(0, color="#DC2626", linewidth=1)
        ax.set_title(f"LightGBM D+{h}: phần dư")
        ax.set_xlabel("Dự báo (m³/s)")
        ax.set_ylabel("Dự báo − quan trắc (m³/s)")
        ax.grid(alpha=0.2)
    fig.suptitle("Chẩn đoán sai số dự báo LightGBM", fontsize=12)
    fig.tight_layout()
    fig.savefig(figures_dir / "forecast_scatter.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / "forecast_scatter.pdf", bbox_inches="tight")
    plt.close(fig)


def _write_findings(
    cfg: dict[str, Any],
    overall: pd.DataFrame,
    by_horizon: pd.DataFrame,
    by_year: pd.DataFrame,
    q2: dict[str, Any],
    q1: dict[str, Any],
    output_path: Path,
) -> None:
    test = overall[overall["split"] == "test"].sort_values("mean_RMSE_7")
    best = test.iloc[0]
    rows = []
    for _, row in test.iterrows():
        rows.append(
            f"| {MODEL_LABELS.get(row['model'], row['model'])} | "
            f"{row['mean_RMSE_7']:.2f} | {row['mean_MAE_7']:.2f} | "
            f"{row['mean_NSE_7']:.3f} | {row['pooled_RMSE']:.2f} | "
            f"{row['pooled_NSE']:.3f} |"
        )
    table = "\n".join(rows)
    lgb = by_horizon[(by_horizon["split"] == "test") & (by_horizon["model"] == "lightgbm_direct")]
    lgb_first = lgb.sort_values("horizon").iloc[0]
    lgb_last = lgb.sort_values("horizon").iloc[-1]
    worst_year = by_year[(by_year["split"] == "test") & (by_year["model"] == "lightgbm_direct")]
    worst_year = worst_year.groupby("target_year")["RMSE"].mean().sort_values(ascending=False)
    text = f"""# Findings

## Q1 — Xu hướng và mùa vụ

- Trung bình tháng thấp nhất là tháng {q1['monthly_mean_min']['month']} ({q1['monthly_mean_min']['value']:.2f} m³/s), cao nhất là tháng {q1['monthly_mean_max']['month']} ({q1['monthly_mean_max']['value']:.2f} m³/s); biên độ trung bình tháng khoảng {q1['monthly_amplitude_mean']:.2f} m³/s.
- Trung bình năm thấp nhất là {q1['yearly_mean_min']['year']} ({q1['yearly_mean_min']['value']:.2f} m³/s), cao nhất là {q1['yearly_mean_max']['year']} ({q1['yearly_mean_max']['value']:.2f} m³/s); biến thiên nhiều năm lớn hơn biên độ mùa vụ trung bình.
- Cần đọc trend theo giai đoạn thay vì kết luận một chiều tăng/giảm cho cả 14 năm.

## Q2 — Lưu lượng cao

- Q95 toàn chuỗi = {q2['threshold']:.2f} m³/s; có {q2['n_days_high']} ngày vượt ngưỡng ({q2['share_days_high'] * 100:.2f}%), tương ứng {q2['n_events']} đợt liên tiếp.
- Đợt dài nhất kéo dài {q2['longest_event_days']} ngày; đỉnh lớn nhất trong các đợt là {q2['max_event_peak']:.2f} m³/s.
- Ngưỡng Z tương đương Q95 là {q2['z_threshold']:.3f}, không phải 1,645; vì vậy không được gọi z > 3 là Top 5%.

## Q3 — Dự báo

| Mô hình | mean RMSE 7 horizon | mean MAE 7 horizon | mean NSE 7 horizon | pooled RMSE | pooled NSE |
|---|---:|---:|---:|---:|---:|
{table}

- Mô hình có mean RMSE thấp nhất trên Test là **{MODEL_LABELS.get(best['model'], best['model'])}** ({best['mean_RMSE_7']:.2f} m³/s).
- LightGBM D+1 có RMSE {lgb_first['RMSE']:.2f} m³/s, NSE {lgb_first['NSE']:.3f}; D+7 có RMSE {lgb_last['RMSE']:.2f} m³/s, NSE {lgb_last['NSE']:.3f}.
- Năm có RMSE trung bình cao nhất của LightGBM trên Test là {int(worst_year.index[0])} ({worst_year.iloc[0]:.2f} m³/s).
- Kết quả chỉ mô tả Test 2022–2023, không phải bảo đảm cho dự báo vận hành hay cảnh báo lũ.
"""
    write_text(output_path, text)


def run_evaluation(
    cfg: dict[str, Any],
    frame: pd.DataFrame,
    run_id: str,
    q1: dict[str, Any],
    q2: dict[str, Any],
) -> dict[str, Any]:
    raw_df = load_raw_csv(resolve_path(cfg, "processed_csv"))
    results_dir = resolve_path(cfg, "results_dir")
    figures_dir = resolve_path(cfg, "figures_dir")
    tables_dir = resolve_path(cfg, "tables_dir")
    checkpoints_dir = resolve_path(cfg, "checkpoints_dir")
    horizon = int(cfg["split"]["horizon"])
    test_origins = _origins(frame, cfg, "test")

    pred_frames = [
        _attach(naive.predict(raw_df, test_origins, horizon), run_id, "test"),
        _attach(seasonal_naive.predict(raw_df, test_origins, horizon), run_id, "test"),
    ]
    models = lightgbm_direct.load_frozen(checkpoints_dir, horizon)
    target_mode = str(cfg["lightgbm"].get("target_mode", "raw"))
    pred_frames.append(
        _attach(
            lightgbm_direct.predict(models, frame, test_origins, horizon, target_mode=target_mode),
            run_id,
            "test",
        )
    )
    predictions = pd.concat(pred_frames, ignore_index=True)
    predictions = predictions.dropna(subset=["y_true", "y_pred"]).copy()
    predictions["origin_date"] = pd.to_datetime(predictions["origin_date"])
    predictions["target_date"] = pd.to_datetime(predictions["target_date"])
    predictions["horizon"] = predictions["horizon"].astype(int)
    predictions.to_csv(tables_dir / "predictions_long.csv", index=False, float_format="%.6f")

    metrics = summarize_metrics(predictions)
    metrics["by_horizon"].to_csv(tables_dir / "metrics_by_horizon.csv", index=False, float_format="%.6f")
    metrics["overall"].to_csv(tables_dir / "metrics_overall.csv", index=False, float_format="%.6f")
    metrics["by_year"].to_csv(tables_dir / "metrics_by_year.csv", index=False, float_format="%.6f")

    _plot_metrics(metrics["by_horizon"], figures_dir)
    _plot_hydrograph(predictions, figures_dir)
    _plot_scatter(predictions, figures_dir)

    illustrative_origin = pd.DatetimeIndex([pd.Timestamp("2023-12-31")])
    illustrative = lightgbm_direct.predict(
        models, frame, illustrative_origin, horizon, target_mode=target_mode
    )
    illustrative.to_csv(tables_dir / "forecast_illustrative_2024.csv", index=False, float_format="%.6f")

    _write_findings(
        cfg,
        metrics["overall"],
        metrics["by_horizon"],
        metrics["by_year"],
        q2,
        q1,
        Path(cfg["_code_dir"]) / "docs" / "findings.md",
    )
    summary = {
        "test_origins": int(len(test_origins)),
        "n_predictions": int(len(predictions)),
        "models": sorted(predictions["model"].unique().tolist()),
        "metrics_test": metrics["overall"][metrics["overall"]["split"] == "test"].to_dict(orient="records"),
        "illustrative_origin": "2023-12-31",
        "gru_status": "not_run_missing_torch",
    }
    write_json(results_dir / "evaluation_summary.json", summary)
    return {"predictions": predictions, **metrics, "summary": summary}
