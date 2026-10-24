from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd

from ..io import write_json
from ..metrics import mae, nse, rmse
from ..features import design_columns


def _sample_params(space: dict[str, list[Any]], rng: random.Random) -> dict[str, Any]:
    params = {key: rng.choice(values) for key, values in space.items()}
    if params["max_depth"] != -1 and params["num_leaves"] > 2 ** int(params["max_depth"]):
        params["num_leaves"] = 2 ** int(params["max_depth"])
    return params


def _params(base: dict[str, Any], sampled: dict[str, Any], seed: int) -> dict[str, Any]:
    params = dict(base)
    params.update(sampled)
    params["seed"] = int(seed)
    params["num_threads"] = int(base.get("n_jobs", 4))
    params["verbosity"] = -1
    params["deterministic"] = True
    params["force_col_wise"] = True
    return params


def _target(y: np.ndarray, q: np.ndarray, mode: str) -> np.ndarray:
    return y - q if mode == "delta" else y


def _to_level(pred: np.ndarray, q: np.ndarray, mode: str) -> np.ndarray:
    return pred + q if mode == "delta" else pred


def validation_search(datasets: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    lgb_cfg = cfg["lightgbm"]
    target_mode = str(lgb_cfg.get("target_mode", "raw"))
    seed = int(cfg["project"]["seed"])
    rng = random.Random(seed)
    n_trials = int(lgb_cfg.get("trials", 8))
    horizon = int(cfg["split"]["horizon"])
    trials: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for trial_id in range(1, n_trials + 1):
        sampled = _sample_params(lgb_cfg["search_space"], rng)
        params = _params(lgb_cfg["base_params"], sampled, seed)
        per_horizon: dict[str, Any] = {}
        for h in range(1, horizon + 1):
            train = datasets["train"][h]
            valid = datasets["validation"][h]
            y_train = _target(train["y"], train["q"], target_mode)
            y_valid = _target(valid["y"], valid["q"], target_mode)
            dtrain = lgb.Dataset(train["X"], label=y_train, free_raw_data=False)
            dvalid = lgb.Dataset(valid["X"], label=y_valid, reference=dtrain, free_raw_data=False)
            callbacks = [
                lgb.early_stopping(int(lgb_cfg["early_stopping_rounds"]), verbose=False),
                lgb.log_evaluation(0),
            ]
            model = lgb.train(
                params,
                dtrain,
                num_boost_round=int(lgb_cfg["num_boost_round"]),
                valid_sets=[dvalid],
                callbacks=callbacks,
            )
            best_iter = int(model.best_iteration or model.current_iteration() or 1)
            pred = _to_level(model.predict(valid["X"], num_iteration=best_iter), valid["q"], target_mode)
            per_horizon[str(h)] = {
                "best_iteration": best_iter,
                "RMSE": rmse(valid["y"], pred),
                "MAE": mae(valid["y"], pred),
                "NSE": nse(valid["y"], pred),
            }
        trial = {
            "trial_id": trial_id,
            "params": sampled,
            "per_horizon": per_horizon,
            "mean_RMSE": float(np.mean([v["RMSE"] for v in per_horizon.values()])),
            "mean_MAE": float(np.mean([v["MAE"] for v in per_horizon.values()])),
            "mean_NSE": float(np.mean([v["NSE"] for v in per_horizon.values()])),
        }
        trials.append(trial)
        if best is None or trial["mean_RMSE"] < best["mean_RMSE"]:
            best = trial

    assert best is not None
    return {
        "best_trial": best,
        "trials": trials,
        "n_trials": len(trials),
        "target_mode": target_mode,
    }


def fit_frozen(
    datasets: dict[str, Any],
    selection: dict[str, Any],
    cfg: dict[str, Any],
    checkpoints_dir: Path,
) -> dict[int, lgb.Booster]:
    lgb_cfg = cfg["lightgbm"]
    target_mode = str(lgb_cfg.get("target_mode", "raw"))
    best = selection["best_trial"]
    params = _params(lgb_cfg["base_params"], best["params"], int(cfg["project"]["seed"]))
    models: dict[int, lgb.Booster] = {}
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    for h in range(1, int(cfg["split"]["horizon"]) + 1):
        data = datasets["refit"][h]
        best_iter = int(best["per_horizon"][str(h)]["best_iteration"])
        dtrain = lgb.Dataset(data["X"], label=_target(data["y"], data["q"], target_mode))
        model = lgb.train(params, dtrain, num_boost_round=best_iter)
        path = checkpoints_dir / f"lightgbm_h{h}.txt"
        model.save_model(str(path))
        models[h] = model
    write_json(
        checkpoints_dir / "lightgbm_feature_order.json",
        {str(h): design_columns(h) for h in range(1, int(cfg["split"]["horizon"]) + 1)},
    )
    write_json(checkpoints_dir / "lightgbm_meta.json", {"target_mode": target_mode})
    return models


def load_frozen(checkpoints_dir: Path, horizon: int) -> dict[int, lgb.Booster]:
    models: dict[int, lgb.Booster] = {}
    for h in range(1, horizon + 1):
        path = checkpoints_dir / f"lightgbm_h{h}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Thiếu model đã khóa: {path}")
        models[h] = lgb.Booster(model_file=str(path))
    return models


def predict(
    models: dict[int, lgb.Booster],
    frame: pd.DataFrame,
    origins: pd.DatetimeIndex,
    horizon: int = 7,
    model_name: str = "lightgbm_direct",
    target_mode: str = "raw",
) -> pd.DataFrame:
    origins = pd.DatetimeIndex(origins).normalize()
    rows: list[dict[str, Any]] = []
    for h in range(1, horizon + 1):
        cols = design_columns(h)
        subset = frame.reindex(origins)[cols]
        valid = subset.notna().all(axis=1)
        if not valid.any():
            continue
        x = subset.loc[valid, cols].to_numpy(dtype=np.float32)
        pred = _to_level(models[h].predict(x), subset.loc[valid, "q"].to_numpy(dtype=float), target_mode)
        for origin, y_pred in zip(subset.index[valid], pred):
            target = origin + pd.Timedelta(days=h)
            y_true = frame.loc[origin, f"y_h{h}"] if origin in frame.index else np.nan
            rows.append(
                {
                    "model": model_name,
                    "origin_date": origin,
                    "target_date": target,
                    "horizon": h,
                    "y_true": float(y_true) if pd.notna(y_true) else None,
                    "y_pred": float(y_pred),
                }
            )
    return pd.DataFrame(rows)


def feature_importance(
    models: dict[int, lgb.Booster],
    checkpoints_dir: Path,
    horizon: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for h in range(1, horizon + 1):
        cols = design_columns(h)
        gains = models[h].feature_importance(importance_type="gain")
        for name, gain in zip(cols, gains):
            rows.append({"horizon": h, "feature": name, "gain": float(gain)})
    table = pd.DataFrame(rows)
    table.to_csv(checkpoints_dir / "lightgbm_feature_importance.csv", index=False, float_format="%.6f")
    return table
