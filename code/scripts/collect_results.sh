#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"

cd "$ROOT"
[[ -x "$PYTHON" ]] || { echo "Thiếu $PYTHON" >&2; exit 1; }
"$PYTHON" -m pytest -q
"$PYTHON" - <<'PY'
import pandas as pd
from pathlib import Path

tables = Path("results/tables")
print("\nTest overall:")
print(pd.read_csv(tables / "metrics_overall.csv").to_string(index=False))
print("\nArtifacts:")
for p in [tables / "predictions_long.csv", tables / "extreme_events.csv",
          Path("results/split_manifest.json"), Path("results/model_selection_full.json")]:
    print(f"  {p} ({p.stat().st_size} bytes)")
PY
