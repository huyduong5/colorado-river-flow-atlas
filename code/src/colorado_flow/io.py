from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

CODE_DIR = Path(__file__).resolve().parents[2]
DATE_FMT = "%Y-%m-%d"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path is not None else CODE_DIR / "configs" / "default.yaml"
    if not cfg_path.is_absolute():
        cfg_path = CODE_DIR / cfg_path
    if not cfg_path.exists():
        raise FileNotFoundError(f"Không tìm thấy config: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_config_path"] = str(cfg_path)
    cfg["_code_dir"] = str(CODE_DIR)
    cfg["_root_dir"] = str(CODE_DIR.parent)
    return cfg


def resolve_path(cfg: dict[str, Any], key: str) -> Path:
    raw = cfg["paths"][key]
    path = Path(raw)
    if not path.is_absolute():
        path = CODE_DIR / path
    return path


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_raw_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy CSV: {path}")
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    required = {"date", "discharge_m3s"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV thiếu cột: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"], format=DATE_FMT, errors="raise")
    df["discharge_m3s"] = pd.to_numeric(df["discharge_m3s"], errors="coerce")
    df = df.sort_values("date", kind="mergesort").reset_index(drop=True)
    df = df.set_index("date")
    df.index.name = "date"
    return df


def ensure_dirs(cfg: dict[str, Any]) -> None:
    for key in (
        "processed_csv",
        "features_csv",
        "results_dir",
        "figures_dir",
        "tables_dir",
        "checkpoints_dir",
        "logs_dir",
        "docs_dir",
        "web_data_dir",
    ):
        path = resolve_path(cfg, key)
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: str | Path, payload: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(_jsonable(payload), fh, ensure_ascii=False, indent=2, allow_nan=False)
        fh.write("\n")
    return path


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path: str | Path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def fmt_date(value: Any) -> str:
    return pd.Timestamp(value).strftime(DATE_FMT)


def fmt_num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "NA"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(value):
        return "NA"
    return f"{value:.{digits}f}"
