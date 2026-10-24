# TASKS

Trạng thái được cập nhật theo sản phẩm thực tế trong thư mục dự án. Không đánh dấu
hoàn tất nếu chưa có tệp/kết quả kiểm chứng.

| ID | Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|---|
| P0.1 | Đọc đề, khóa giới hạn 5 trang và thông tin tác giả | Hoàn tất | `plan.md`, `code/docs/requirements.md` |
| P0.2 | Tạo skeleton `code/`, `latex/`, `deliverables/` | Hoàn tất | cấu trúc thư mục |
| P1.1 | Audit dữ liệu, checksum, Q95 | Hoàn tất | `code/results/data_quality.json` |
| P1.2 | Kiểm tra lịch, thiếu/trùng, giá trị bất thường | Hoàn tất | `code/tests/test_data_contract.py` |
| P2.1 | Q1: trung bình tháng/năm, STL, ACF | Hoàn tất | `code/results/q1_summary.json`, `seasonality_metrics.json` |
| P2.2 | Hình Q1 | Hoàn tất | `code/results/figures/trend_seasonality.pdf` |
| P3.1 | Q2: Q95, Z tương đương, gộp đợt | Hoàn tất | `code/results/q2_summary.json` |
| P3.2 | Top 5 đợt và hình Q2 | Hoàn tất | `code/results/tables/extreme_events_top5.csv` |
| P4.1 | Chia Train/Validation/Test theo thời gian | Hoàn tất | `code/results/split_manifest.json` |
| P4.2 | Feature matrix, kiểm tra không rò rỉ | Hoàn tất | `code/tests/test_features_no_leakage.py` |
| P5.1 | Baseline Naive, Seasonal Naive | Hoàn tất | `code/results/metrics_overall.csv` |
| P5.2 | LightGBM direct 7, tìm tham số trên Validation | Hoàn tất | `code/results/model_selection_full.json` |
| P6.1 | GRU direct 7 | Bỏ qua có ghi chú | Không có PyTorch; `code/src/colorado_flow/models/gru.py` là placeholder |
| P7.1 | Freeze model, refit, dự báo Test | Hoàn tất | `code/results/checkpoints/`, `predictions_long.csv` |
| P7.2 | Đánh giá RMSE/MAE/NSE, hình dự báo | Hoàn tất | `code/results/tables/metrics_*`, `figures/forecast_*` |
| P8.1 | Thiết kế website 8 trang, dữ liệu thật | Hoàn tất | `code/web/src/pages/` |
| P8.2 | Build + smoke test dữ liệu web | Hoàn tất | `npm run build`, `npm run test` |
| P9.1 | Kiểm chứng số liệu web khớp CSV | Hoàn tất | `code/tests/test_export_consistency.py`, `code/web/tests/smoke.mjs` |
| P9.2 | Kiểm tra schema JSON lúc chạy + màn hình lỗi | Hoàn tất | `code/web/src/lib/api.ts` |
| P9.3 | Chart zoom/restore/tải PNG, forecast slider | Hoàn tất | `code/web/src/lib/charts.ts`, `ForecastPage.tsx` |
| P9.4 | Responsive 375/768/1440, không tràn ngang | Hoàn tất | ảnh trong `code/docs/screenshots/`; CDP đo `scrollWidth` |
| P9.5 | Wireframe và luồng sử dụng | Hoàn tất | `code/docs/wireframes.md` |
| P10.1 | Source LaTeX, bảng/hình tự sinh | Hoàn tất | `latex/main.tex`, `latex/sections/`, `latex/tables/` |
| P10.2 | PDF ≤ 5 trang | Hoàn tất | `pdfinfo`: 5 trang; `deliverables/23001524_DUONGQUANGHUY_BAITAP2.pdf` |
| P11.0 | Test source ZIP từ bản giải nén | Hoàn tất | 14 test pass với `PYTHONPATH=src` |
| P11.1 | ZIP Overleaf biên dịch độc lập | Hoàn tất | Tectonic compile, `pdfinfo` = 5 trang |
| P11.2 | ZIP source + kết quả | Hoàn tất | `deliverables/source_code.zip` |
| P11.3 | Checksum deliverable | Hoàn tất | `cd deliverables && sha256sum -c SHA256SUMS` |
| P11.4 | Secret scan | Hoàn tất | Không có `.env`, key, token, mật khẩu thật |
| P11.5 | Publish website công khai | Hoàn tất | GitHub Pages: https://huyduong5.github.io/colorado-river-flow-atlas/; workflow deploy pass; HTTP 200 |
| P11.6 | Clean-room reproduction | Hoàn tất | venv mới từ `requirements.lock.txt`; 14 test pass; pipeline tái tạo đúng metrics/predictions |
| P12.1 | Tạo GitHub public | Hoàn tất | https://github.com/huyduong5/colorado-river-flow-atlas |
| P12.2 | GitHub Actions deploy Pages | Hoàn tất | `.github/workflows/deploy-pages.yml`; run 40113065315 pass |
| P12.3 | QR website và GitHub | Hoàn tất | `latex/assets/qr_website.png`, `latex/assets/qr_github.png` |
| P13.1 | Sinh bảng/hình báo cáo đầy đủ | Hoàn tất | `latex_full/tables/` (14 bảng), `latex_full/figures/` (14 hình), `latex_full/generated/assets_manifest.json` |
| P13.2 | Tích hợp export full vào pipeline | Hoàn tất | `export_latex_full.py`; `--stage export` sinh cả `latex/` và `latex_full/` |
| P13.3 | Kiểm tra asset compile | Hoàn tất | Tectonic compile bộ asset 5 trang; 15 Python test pass; ảnh PNG đã kiểm tra |

## Ghi chú

- Không có kết quả GRU trong báo cáo; đây là hạng mục mở rộng, không phải kết quả giả.
- PDF được biên dịch bằng Tectonic (XeLaTeX) trên máy local; Overleaf dùng cùng source.
- Mọi số liệu trong PDF/website lấy từ cùng `run_id` `run-20261024T160504+0000`.
