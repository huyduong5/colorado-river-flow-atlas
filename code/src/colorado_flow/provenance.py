from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import __version__
from .io import read_json, sha256_file, write_json


def package_versions() -> dict[str, str]:
    import lightgbm
    import matplotlib
    import scipy
    import sklearn
    import statsmodels

    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "statsmodels": statsmodels.__version__,
        "lightgbm": lightgbm.__version__,
        "matplotlib": matplotlib.__version__,
    }


def make_run_manifest(cfg: dict[str, Any], dataset_hash: str, created_at: str | None = None) -> dict[str, Any]:
    created_at = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    config_path = Path(cfg["_config_path"])
    return {
        "schema_version": "1.0",
        "run_id": f"run-{created_at.replace(':', '').replace('-', '')}",
        "created_at_utc": created_at,
        "project_version": __version__,
        "dataset_hash": dataset_hash,
        "config_path": str(config_path),
        "config_hash": sha256_file(config_path),
        "seed": int(cfg["project"]["seed"]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "versions": package_versions(),
        "split": cfg["split"],
        "threshold": cfg["threshold"],
    }


def load_or_create_manifest(cfg: dict[str, Any], dataset_hash: str) -> dict[str, Any]:
    path = Path(cfg["_code_dir"]) / "results" / "run_manifest.json"
    if path.exists():
        manifest = read_json(path)
        if manifest.get("dataset_hash") == dataset_hash:
            return manifest
    manifest = make_run_manifest(cfg, dataset_hash)
    write_json(path, manifest)
    return manifest
