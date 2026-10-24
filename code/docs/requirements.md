# Yêu cầu và phạm vi

## Nguồn

- `Yêu cầu BÀI TẬP 2.docx`: đề chính thức.
- `colorado_river_flow.csv`: dữ liệu lưu lượng ngày.
- `23001524_DUONGQUANGHUY_BAITAP1.pdf` và `Tham khao mau bao cao bai tap 1.pdf`:
  tham khảo trình bày.
- `logo_dhkhtn.jpg`: logo trường, chỉ dùng nhỏ hoặc bỏ.

## Sản phẩm bắt buộc

1. Q1: mô tả xu hướng và mùa vụ của chuỗi lưu lượng.
2. Q2: xác định các ngày/đợt lưu lượng cao theo Top 5% (Q95), bảng Top 5.
3. Q3: dự báo 7 ngày với ít nhất một mô hình học máy (LightGBM hoặc GRU), so sánh
   baseline; báo cáo RMSE, MAE, NSE trên Test 2022–2023.
4. PDF tối đa 5 trang, có bìa, nội dung Q1–Q3, bảng/hình và tài liệu tham khảo.

## Sản phẩm bổ sung

- Website tra cứu dữ liệu và kết quả.
- Source LaTeX upload Overleaf.
- Source code, config, test, lockfile và kết quả để tái lập.

## Ràng buộc

- Không dùng SSH/server; huấn luyện CPU local.
- Không lưu host/user/password/token trong artifact.
- Không xáo trộn dữ liệu; Test 2022–2023 tách biệt.
- Không tạo kết quả giả; GRU không chạy thì ghi rõ.
- Không tinh chỉnh mô hình trên Test.

## Tiêu chí nghiệm thu

| Mã | Yêu cầu | Bằng chứng |
|---|---|---|
| Q1 | Trend/seasonality có hình, số liệu | `q1_summary.json`, `trend_seasonality.pdf` |
| Q2 | Q95, đợt, Top 5 | `q2_summary.json`, `extreme_events_top5.csv` |
| Q3 | Baseline + LightGBM, 7 horizon, metrics | `metrics_*`, `predictions_long.csv` |
| Q4 | PDF ≤ 5 trang | `pdfinfo` trả 5 trang |
| U1 | Website dùng dữ liệu thật | `web/public/data`, smoke test |
| U2 | LaTeX độc lập | `latex/main.tex`, `latex_overleaf.zip` |
| U3 | Source tái lập | `source_code.zip`, README, lockfile |
