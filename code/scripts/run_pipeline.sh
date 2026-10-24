#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Không thấy Python tại $PYTHON. Chạy: cd code && uv venv --system-site-packages .venv" >&2
  exit 1
fi

cd "$ROOT"
"$PYTHON" -m colorado_flow.pipeline --stage "${1:-all}" "${@:2}"
