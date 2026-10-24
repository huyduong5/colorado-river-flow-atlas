from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from .io import load_raw_csv, read_json, resolve_path, write_json


MODEL_LABELS = {
    "naive": "Naive persistence",
    "seasonal_naive_365": "Seasonal Naive 365",
    "lightgbm_direct": "LightGBM direct 7 (delta)",
}


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.replace({pd.NA: None}).to_dict(orient="records")


def export_web(cfg: dict[str, Any], manifest: dict[str, Any]) -> Path:
    results_dir = resolve_path(cfg, "results_dir")
    tables_dir = resolve_path(cfg, "tables_dir")
    web_dir = resolve_path(cfg, "web_data_dir")
    downloads_dir = web_dir.parent / "downloads"
    web_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    raw = load_raw_csv(resolve_path(cfg, "processed_csv"))
    daily = pd.DataFrame({"date": raw.index.strftime("%Y-%m-%d"), "q": raw["discharge_m3s"].astype(float)})
    monthly = pd.read_csv(tables_dir / "monthly_stats.csv")
    yearly = pd.read_csv(tables_dir / "yearly_stats.csv")
    monthly_by_year = pd.read_csv(tables_dir / "monthly_by_year.csv")
    events = pd.read_csv(tables_dir / "extreme_events.csv")
    top5 = pd.read_csv(tables_dir / "extreme_events_top5.csv")
    predictions = pd.read_csv(tables_dir / "predictions_long.csv", parse_dates=["origin_date", "target_date"])
    metrics_by_horizon = pd.read_csv(tables_dir / "metrics_by_horizon.csv")
    metrics_overall = pd.read_csv(tables_dir / "metrics_overall.csv")
    metrics_by_year = pd.read_csv(tables_dir / "metrics_by_year.csv")
    illustrative = pd.read_csv(tables_dir / "forecast_illustrative_2024.csv", parse_dates=["origin_date", "target_date"])

    q1 = read_json(results_dir / "q1_summary.json")
    q2 = read_json(results_dir / "q2_summary.json")
    seasonality = read_json(results_dir / "seasonality_metrics.json")
    evaluation = read_json(results_dir / "evaluation_summary.json")

    write_json(web_dir / "daily.json", _records(daily))
    write_json(web_dir / "monthly.json", _records(monthly))
    write_json(web_dir / "yearly.json", _records(yearly))
    write_json(
        web_dir / "heatmap.json",
        {
            "years": monthly_by_year["year"].astype(int).tolist(),
            "values": monthly_by_year.drop(columns=["year"]).to_numpy().round(3).tolist(),
        },
    )
    write_json(
        web_dir / "extremes.json",
        {
            "summary": q2,
            "events": _records(events),
            "top5": _records(top5),
        },
    )
    write_json(
        web_dir / "metrics.json",
        {
            "overall": _records(metrics_overall),
            "by_horizon": _records(metrics_by_horizon),
            "by_year": _records(metrics_by_year),
        },
    )
    write_json(
        web_dir / "predictions.json",
        {
            "models": sorted(predictions["model"].unique().tolist()),
            "labels": MODEL_LABELS,
            "rows": _records(predictions),
        },
    )
    write_json(web_dir / "forecast_illustrative.json", _records(illustrative))
    write_json(
        web_dir / "seasonality.json",
        {
            "summary": seasonality,
            "q1": q1,
        },
    )
    write_json(web_dir / "findings.json", evaluation)

    for name in (
        "predictions_long.csv",
        "metrics_overall.csv",
        "metrics_by_horizon.csv",
        "metrics_by_year.csv",
        "extreme_events.csv",
        "monthly_stats.csv",
        "yearly_stats.csv",
    ):
        shutil.copy2(tables_dir / name, downloads_dir / name)
    shutil.copy2(resolve_path(cfg, "processed_csv"), downloads_dir / "colorado_river_flow_processed.csv")

    files = sorted(p.name for p in web_dir.glob("*.json")) + sorted(p.name for p in downloads_dir.glob("*"))
    web_manifest = {
        "schema_version": "1.0",
        "run_id": manifest["run_id"],
        "dataset_hash": manifest["dataset_hash"],
        "created_at_utc": manifest["created_at_utc"],
        "models": sorted(predictions["model"].unique().tolist()),
        "model_labels": MODEL_LABELS,
        "date_scopes": {
            "observations": {"start": str(raw.index.min().date()), "end": str(raw.index.max().date())},
            "test": {"start": cfg["split"]["test_start"], "end": cfg["split"]["test_end"]},
        },
        "definitions": {
            "threshold_scope": cfg["threshold"]["scope"],
            "threshold_quantile": cfg["threshold"]["quantile"],
            "horizon_days": int(cfg["split"]["horizon"]),
            "metrics": ["RMSE", "MAE", "NSE"],
        },
        "files": files,
    }
    write_json(web_dir / "manifest.json", web_manifest)

    latest_pdf = Path(cfg["_root_dir"]) / "deliverables" / "23001524_DUONGQUANGHUY_BAITAP2.pdf"
    if latest_pdf.exists():
        shutil.copy2(latest_pdf, downloads_dir / latest_pdf.name)
    return web_dir
