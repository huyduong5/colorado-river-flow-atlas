# Tái lập

## Phiên bản đã kiểm tra

- Python 3.12.3; `uv` 0.11.22.
- numpy 2.5.4, pandas 3.1.0, scipy 1.18.1, scikit-learn 1.9.1, statsmodels 0.15.0,
  lightgbm 4.7.0, matplotlib 3.11.2, pytest 9.1.1, PyYAML 6.0.3.
- Node 22.18.0, npm 10.9.3, Vite 8.3.5, React 19.3.1, ECharts 6.1.0.
- PDF: Tectonic 0.17.0 (XeLaTeX), 5 trang.

## Cài đặt

```bash
cd code
uv venv --system-site-packages .venv
uv pip install --python .venv/bin/python -e .
```

Nếu không có `uv`, dùng `python3 -m venv .venv` (máy này từng lỗi ensurepip) rồi
`pip install -r requirements.lock.txt`.

## Chạy pipeline

```bash
cd code
.venv/bin/python -m pytest -q
.venv/bin/python -m colorado_flow.pipeline --stage all
```

Thứ tự stage: `audit → eda → features → train → freeze → evaluate → export`.

## Kết quả kỳ vọng

- `results/data_quality.json`: 5.113 dòng, hash khớp.
- `split_manifest.json`: 3.615 / 725 / 724 / 4.346.
- `model_selection_full.json`: best trial và validation metrics.
- `metrics_overall.csv`: 3 mô hình trên Test; Naive mean RMSE 5,307564,
  LightGBM mean RMSE 5,325013.
- `predictions_long.csv`: 15.204 dòng (3 mô hình × 5.068 cặp).
- `web/public/data/*.json`: dữ liệu website.
- Run hiện tại: `run-20261024T160504+0000`; run_id này phải khớp
  `results/run_manifest.json`, `latex/generated/numbers.tex` và
  `web/public/data/manifest.json`.

## Clean-room check

Đã kiểm tra bằng venv mới, không dùng `.venv` hay `node_modules` của dự án:

```bash
uv venv /tmp/opencode/clean-venv --python 3.12
uv pip install --python /tmp/opencode/clean-venv/bin/python \
  -r requirements.lock.txt -e .
/tmp/opencode/clean-venv/bin/python -m pytest -q
```

Kết quả: 14 test pass. Một bản sao source không có `.venv`, `node_modules`, `dist`
chạy `python -m colorado_flow.pipeline --stage all` bằng venv sạch đã tái tạo đúng
metrics của run cuối; chạy lặp lại cho cùng dự báo (khác duy nhất cột `run_id`).

## Website

```bash
cd code/web
npm install
npm test
npm run build
python3 -m http.server 4173 --directory dist
```

## PDF

Có TeX:

```bash
cd latex
xelatex main.tex
xelatex main.tex
pdfinfo main.pdf | grep Pages
```

Máy này không có TeX hệ thống; PDF được tạo bằng Tectonic:

```bash
tectonic -X compile main.tex --outdir build
```

Hoặc upload `deliverables/latex_overleaf.zip` lên Overleaf, chọn XeLaTeX, compile
`main.tex`. PDF phải còn ≤ 5 trang.

## Lưu ý

- Không chạy lại `train` với cấu hình khác rồi trộn kết quả với PDF cũ.
- `run_manifest.json` phải khớp `run_id` trong `latex/generated/numbers.tex`,
  `web/public/data/manifest.json` và `metrics_*`.
- `results/checkpoints/` cần thiết để `freeze`/`evaluate` không train lại.
