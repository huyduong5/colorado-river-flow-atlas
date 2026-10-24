from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .audit import run_audit
from .datasets import build_datasets
from .descriptive import run_descriptive
from .evaluation import run_evaluation
from .export_latex_full import export_latex_full
from .export_web import export_web
from .extremes import run_extremes
from .features import load_feature_frame, run_features, split_masks
from .io import (
    ensure_dirs,
    load_config,
    load_raw_csv,
    read_json,
    resolve_path,
    sha256_file,
    write_json,
)
from .metrics import summarize_metrics
from .models import lightgbm_direct, naive, seasonal_naive
from .provenance import load_or_create_manifest
from .seasonality import run_seasonality
from .splits import run_splits


def _log(message: str) -> None:
    print(f"[pipeline] {message}", flush=True)


def _validation_summary(
    cfg: dict[str, Any],
    frame: pd.DataFrame,
    datasets: dict[str, Any],
    selection: dict[str, Any],
) -> pd.DataFrame:
    raw = load_raw_csv(resolve_path(cfg, "processed_csv"))
    origins = pd.DatetimeIndex(frame.index[split_masks(frame, cfg)["validation"]])
    horizon = int(cfg["split"]["horizon"])
    pred_frames = [
        naive.predict(raw, origins, horizon),
        seasonal_naive.predict(raw, origins, horizon),
    ]
    preds = pd.concat(pred_frames, ignore_index=True).dropna(subset=["y_true", "y_pred"])
    preds["run_id"] = "validation"
    preds["split"] = "validation"
    metrics = summarize_metrics(preds)
    rows = []
    for _, row in metrics["overall"].iterrows():
        rows.append(
            {
                "model": row["model"],
                "split": "validation",
                "mean_RMSE_7": row["mean_RMSE_7"],
                "mean_MAE_7": row["mean_MAE_7"],
                "mean_NSE_7": row["mean_NSE_7"],
                "pooled_RMSE": row["pooled_RMSE"],
                "pooled_MAE": row["pooled_MAE"],
                "pooled_NSE": row["pooled_NSE"],
                "n_origins": row["n_origins"],
            }
        )
    best = selection["best_trial"]
    rows.append(
        {
            "model": "lightgbm_direct",
            "split": "validation",
            "mean_RMSE_7": best["mean_RMSE"],
            "mean_MAE_7": best["mean_MAE"],
            "mean_NSE_7": best["mean_NSE"],
            "pooled_RMSE": np.nan,
            "pooled_MAE": np.nan,
            "pooled_NSE": np.nan,
            "n_origins": int(len(datasets["validation"][1]["origin_dates"])),
        }
    )
    return pd.DataFrame(rows)


def _save_selection(
    cfg: dict[str, Any],
    manifest: dict[str, Any],
    selection: dict[str, Any],
    validation_summary: pd.DataFrame,
) -> None:
    results_dir = resolve_path(cfg, "results_dir")
    tables_dir = resolve_path(cfg, "tables_dir")
    payload = {
        "run_id": manifest["run_id"],
        "selection_metric": "mean_RMSE_7 trên Validation 2020-2021",
        "target_mode": selection.get("target_mode", "raw"),
        "best_trial": selection["best_trial"],
        "n_trials": selection["n_trials"],
        "gru_status": "not_run_missing_torch",
    }
    write_json(results_dir / "model_selection.json", payload)
    write_json(
        results_dir / "model_selection_full.json",
        {
            **payload,
            "trials": selection["trials"],
            "validation_summary": validation_summary.to_dict(orient="records"),
        },
    )

    trial_rows = []
    for trial in selection["trials"]:
        row = {"trial_id": trial["trial_id"], **trial["params"]}
        row.update(
            {
                "mean_RMSE": trial["mean_RMSE"],
                "mean_MAE": trial["mean_MAE"],
                "mean_NSE": trial["mean_NSE"],
            }
        )
        for h, values in trial["per_horizon"].items():
            row[f"rmse_h{h}"] = values["RMSE"]
            row[f"best_iter_h{h}"] = values["best_iteration"]
        trial_rows.append(row)
    pd.DataFrame(trial_rows).to_csv(tables_dir / "lightgbm_trials.csv", index=False, float_format="%.6f")
    validation_summary.to_csv(tables_dir / "metrics_validation.csv", index=False, float_format="%.6f")


def run_all(cfg: dict[str, Any]) -> None:
    ensure_dirs(cfg)
    raw_path = resolve_path(cfg, "raw_csv")
    raw_hash = sha256_file(raw_path)
    manifest = load_or_create_manifest(cfg, raw_hash)
    _log(f"run_id={manifest['run_id']} dataset_hash={raw_hash[:12]}")

    _log("audit")
    run_audit(cfg)
    processed = load_raw_csv(resolve_path(cfg, "processed_csv"))

    _log("eda: descriptive")
    q1 = run_descriptive(cfg)
    _log("eda: seasonality")
    run_seasonality(cfg)
    _log("eda: extremes")
    q2 = run_extremes(cfg)

    _log("splits + features")
    run_splits(cfg, processed)
    frame = run_features(cfg, processed)

    _log("train: LightGBM validation search")
    datasets = build_datasets(frame, cfg)
    selection = lightgbm_direct.validation_search(datasets, cfg)
    validation_summary = _validation_summary(cfg, frame, datasets, selection)
    _save_selection(cfg, manifest, selection, validation_summary)
    _log(
        f"best trial={selection['best_trial']['trial_id']} "
        f"mean_RMSE={selection['best_trial']['mean_RMSE']:.3f}"
    )

    _log("freeze: refit 2010-2021")
    models = lightgbm_direct.fit_frozen(
        datasets, selection, cfg, resolve_path(cfg, "checkpoints_dir")
    )
    lightgbm_direct.feature_importance(
        models, resolve_path(cfg, "checkpoints_dir"), int(cfg["split"]["horizon"])
    )

    _log("evaluate: rolling-origin Test 2022-2023")
    run_evaluation(cfg, frame, manifest["run_id"], q1, q2)

    _log("export web + latex")
    export_web(cfg, manifest)
    export_latex_full(cfg, manifest)
    _log("done")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline phân tích và dự báo lưu lượng sông Colorado")
    parser.add_argument("--config", default=None, help="Đường dẫn config YAML")
    parser.add_argument(
        "--stage",
        default="all",
        choices=["all", "audit", "eda", "features", "train", "freeze", "evaluate", "export"],
    )
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    ensure_dirs(cfg)
    raw_hash = sha256_file(resolve_path(cfg, "raw_csv"))
    manifest = load_or_create_manifest(cfg, raw_hash)

    if args.stage == "all":
        run_all(cfg)
        return 0

    if args.stage == "audit":
        run_audit(cfg)
    elif args.stage == "eda":
        processed = load_raw_csv(resolve_path(cfg, "processed_csv"))
        run_descriptive(cfg)
        run_seasonality(cfg)
        run_extremes(cfg)
    elif args.stage == "features":
        processed = load_raw_csv(resolve_path(cfg, "processed_csv"))
        run_splits(cfg, processed)
        run_features(cfg, processed)
    elif args.stage == "train":
        frame = load_feature_frame(cfg)
        datasets = build_datasets(frame, cfg)
        selection = lightgbm_direct.validation_search(datasets, cfg)
        validation_summary = _validation_summary(cfg, frame, datasets, selection)
        _save_selection(cfg, manifest, selection, validation_summary)
    elif args.stage == "freeze":
        frame = load_feature_frame(cfg)
        datasets = build_datasets(frame, cfg)
        selection = read_json(resolve_path(cfg, "results_dir") / "model_selection_full.json")
        models = lightgbm_direct.fit_frozen(
            datasets, selection, cfg, resolve_path(cfg, "checkpoints_dir")
        )
        lightgbm_direct.feature_importance(
            models, resolve_path(cfg, "checkpoints_dir"), int(cfg["split"]["horizon"])
        )
    elif args.stage == "evaluate":
        frame = load_feature_frame(cfg)
        q1 = read_json(resolve_path(cfg, "results_dir") / "q1_summary.json")
        q2 = read_json(resolve_path(cfg, "results_dir") / "q2_summary.json")
        run_evaluation(cfg, frame, manifest["run_id"], q1, q2)
    elif args.stage == "export":
        export_web(cfg, manifest)
        export_latex_full(cfg, manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
