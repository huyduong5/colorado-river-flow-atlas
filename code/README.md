# Colorado Flow — pipeline phân tích

Mã nguồn Python cho Q1 (xu hướng/mùa vụ), Q2 (cực trị Q95) và Q3 (dự báo 7 ngày),
cùng website React đọc kết quả đã xuất.

## Môi trường

Máy đã kiểm tra: Python 3.12.3, Node 22.18.0, npm 10.9.3, `uv` 0.11.22.

```bash
cd code
uv venv --system-site-packages .venv
uv pip install --python .venv/bin/python -e .
```

Hoặc dùng phiên bản đã khóa:

```bash
.venv/bin/python -m pip install -r requirements.lock.txt
```

Không commit `.venv/`, `node_modules/`, `dist/`, cache.

## Lệnh chính

```bash
# Toàn bộ pipeline: audit -> eda -> features -> train -> freeze -> evaluate -> export
.venv/bin/python -m colorado_flow.pipeline --stage all

# Từng stage
.venv/bin/python -m colorado_flow.pipeline --stage audit
.venv/bin/python -m colorado_flow.pipeline --stage eda
.venv/bin/python -m colorado_flow.pipeline --stage features
.venv/bin/python -m colorado_flow.pipeline --stage train
.venv/bin/python -m colorado_flow.pipeline --stage freeze
.venv/bin/python -m colorado_flow.pipeline --stage evaluate
.venv/bin/python -m colorado_flow.pipeline --stage export

Stage `export` sinh cả báo cáo ngắn trong `latex/` và bộ asset báo cáo đầy đủ
trong `latex_full/` (bảng, hình, số liệu và manifest).

# Tests
.venv/bin/python -m pytest -q
```

## Kết quả

- `results/data_quality.json`, `q1_summary.json`, `q2_summary.json`,
  `seasonality_metrics.json`, `split_manifest.json`.
- `results/tables/`: metrics, top events, monthly/yearly stats, predictions.
- `results/figures/`: hình PDF cho báo cáo.
- `results/checkpoints/`: model LightGBM đã freeze và feature order/importance.
- `results/model_selection_full.json`: trial và validation metrics.
- `results/run_manifest.json`: run hiện tại, hash dữ liệu, seed.

Run hiện tại: `run-20261024T160504+0000`.

## Cấu hình

`configs/default.yaml` khóa split, feature, LightGBM và đường dẫn. Mục tiêu LightGBM
đang là `delta` (`q(t+h) - q(t)`), sau đó cộng lại `q(t)`; đây là biến thể direct 7
được chọn trên Validation, không phải kết quả chọn theo Test.

## Website

```bash
cd web
npm install
npm test
npm run build
npm run dev
```

Website đọc JSON trong `web/public/data/`; `npm run build` xuất `web/dist/`. Link tải
trong trang Downloads trỏ tới `public/downloads/` (CSV, PDF, ZIP khi có).

## Ghi chú khoa học

- Chia thời gian: Train 2010–2019, Validation 2020–2021, Test 2022–2023; không xáo trộn.
- Test chỉ dùng để báo cáo, không dùng chọn mô hình.
- GRU chưa chạy vì không có PyTorch; `models/gru.py` là placeholder, không tạo kết quả giả.
- Kết quả là backtest, không phải dự báo vận hành.
