# Từ điển dữ liệu

## Dữ liệu gốc

`data/raw/colorado_river_flow.csv`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `date` | ngày | Ngày quan sát, 2010-01-01 → 2023-12-31 |
| `discharge_m3s` | số thực | Lưu lượng, m³/s |

## Dữ liệu đã xử lý

`data/processed/colorado_river_flow_processed.csv`

| Cột | Ý nghĩa |
|---|---|
| `date` | Ngày, index duy nhất, đủ lịch |
| `discharge_m3s` | Lưu lượng, m³/s |

## Feature matrix

`data/processed/forecast_features.csv`, mỗi dòng là một ngày gốc.

| Nhóm | Ví dụ | Quy tắc |
|---|---|---|
| Lag | `lag_1`, `lag_2`, `lag_3`, `lag_7`, `lag_14`, `lag_21`, `lag_28`, `lag_30` | Chỉ dùng giá trị quá khứ |
| Rolling | `roll_mean_7`, `roll_std_30`, … | Cửa sổ kết thúc tại ngày gốc |
| Lịch ngày gốc | `doy_sin`, `doy_cos`, `month_sin`, `month_cos` | Tính từ ngày gốc |
| Lịch mục tiêu | `target_doy_h1`, `target_month_h7`, … | Tính từ ngày gốc + h, không dùng dữ liệu tương lai |
| Target | `y_h1` … `y_h7` | Lưu lượng thực tế tại ngày mục tiêu |

Kiểm tra không rò rỉ: thay đổi giá trị sau ngày gốc không làm đổi feature tại ngày gốc
(`tests/test_features_no_leakage.py`).

## Kết quả dự báo

`results/tables/predictions_long.csv`

| Cột | Ý nghĩa |
|---|---|
| `run_id` | Mã lần chạy |
| `model` | `naive`, `seasonal_naive_365`, `lightgbm_direct` |
| `origin_date` | Ngày gốc |
| `target_date` | Ngày mục tiêu = origin + horizon |
| `horizon` | 1…7 |
| `y_true` | Giá trị thực tế |
| `y_pred` | Giá trị dự báo |
| `split` | `validation` hoặc `test` |

`results/tables/metrics_overall.csv`, `metrics_by_horizon.csv`, `metrics_by_year.csv`
chứa RMSE, MAE, NSE; quy ước `mean_*` là trung bình 7 horizon, `pooled_*` tính trên
toàn bộ cặp.

## Cực trị

`results/tables/extreme_events.csv`

| Cột | Ý nghĩa |
|---|---|
| `event_id` | Mã đợt |
| `start_date`, `end_date` | Khoảng ngày liên tiếp vượt Q95 |
| `duration_days` | Số ngày lịch |
| `peak_date`, `peak_flow` | Ngày và giá trị đỉnh trong đợt |
| `threshold_value`, `threshold_scope` | Ngưỡng và phạm vi tính |

`q2_summary.json` chứa threshold, z tương đương, số ngày, số đợt, đợt dài nhất và đỉnh
lớn nhất.
