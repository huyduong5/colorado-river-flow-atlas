#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DELIVERABLES="$ROOT/deliverables"
PDF="$DELIVERABLES/23001524_DUONGQUANGHUY_BAITAP2.pdf"
LATEX_ZIP="$DELIVERABLES/latex_overleaf.zip"
SOURCE_ZIP="$DELIVERABLES/source_code.zip"
SUBMISSION_ZIP="$DELIVERABLES/submission.zip"

cd "$ROOT"
mkdir -p "$DELIVERABLES" code/web/public/downloads code/web/dist/downloads

if [[ -f "$ROOT/latex/main.pdf" ]]; then
  cp "$ROOT/latex/main.pdf" "$PDF"
elif [[ ! -f "$PDF" ]]; then
  echo "Không tìm thấy PDF. Đặt PDF vào $PDF hoặc biên dịch latex/main.tex trước." >&2
  exit 1
fi

cp "$PDF" code/web/public/downloads/bao_cao.pdf

rm -f "$LATEX_ZIP"
(
  cd latex
  zip -rq "$LATEX_ZIP" \
    main.tex metadata.tex latexmkrc references.bib README_OVERLEAF.md \
    generated sections tables figures assets \
    -x '*.aux' '*.log' '*.out' '*.synctex.gz' 'main.pdf'
)
cp "$LATEX_ZIP" code/web/public/downloads/latex_overleaf.zip

if [[ -d code/web/node_modules ]]; then
  npm --prefix code/web run build
fi

rm -f "$SOURCE_ZIP"
zip -rq "$SOURCE_ZIP" \
  code README.md TASKS.md plan.md \
  -x 'code/.venv/*' \
     'code/web/node_modules/*' \
     'code/**/__pycache__/*' \
     'code/.pytest_cache/*' \
     'code/**/*.egg-info/*' \
     'code/web/public/downloads/*.zip' \
     'code/web/dist/downloads/*.zip' \
     'code/results/logs/*.log' \
     'code/data/interim/*'
cp "$SOURCE_ZIP" code/web/public/downloads/source_code.zip
cp "$SOURCE_ZIP" code/web/dist/downloads/source_code.zip

rm -f "$SUBMISSION_ZIP"
(
  cd "$DELIVERABLES"
  zip -jq "$SUBMISSION_ZIP" \
    "$(basename "$PDF")" \
    "$(basename "$LATEX_ZIP")" \
    "$(basename "$SOURCE_ZIP")" \
    "$ROOT/README.md"
)

(
  cd "$DELIVERABLES"
  sha256sum \
    "$(basename "$PDF")" \
    "$(basename "$LATEX_ZIP")" \
    "$(basename "$SOURCE_ZIP")" \
    "$(basename "$SUBMISSION_ZIP")" > SHA256SUMS
)

echo "Đã đóng gói:"
ls -lh "$DELIVERABLES"
echo
cat "$DELIVERABLES/SHA256SUMS"
