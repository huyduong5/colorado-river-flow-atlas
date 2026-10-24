# Findings

## Q1 — Xu hướng và mùa vụ

- Trung bình tháng thấp nhất là tháng 9 (292.32 m³/s), cao nhất là tháng 11 (300.16 m³/s); biên độ trung bình tháng khoảng 7.84 m³/s.
- Trung bình năm thấp nhất là 2010 (129.01 m³/s), cao nhất là 2017 (411.57 m³/s); biến thiên nhiều năm lớn hơn biên độ mùa vụ trung bình.
- Cần đọc trend theo giai đoạn thay vì kết luận một chiều tăng/giảm cho cả 14 năm.

## Q2 — Lưu lượng cao

- Q95 toàn chuỗi = 417.23 m³/s; có 256 ngày vượt ngưỡng (5.01%), tương ứng 15 đợt liên tiếp.
- Đợt dài nhất kéo dài 90 ngày; đỉnh lớn nhất trong các đợt là 457.49 m³/s.
- Ngưỡng Z tương đương Q95 là 1.224, không phải 1,645; vì vậy không được gọi z > 3 là Top 5%.

## Q3 — Dự báo

| Mô hình | mean RMSE 7 horizon | mean MAE 7 horizon | mean NSE 7 horizon | pooled RMSE | pooled NSE |
|---|---:|---:|---:|---:|---:|
| Naive persistence | 5.31 | 4.16 | 0.881 | 5.50 | 0.882 |
| LightGBM direct 7 (delta) | 5.33 | 4.17 | 0.881 | 5.52 | 0.881 |
| Seasonal Naive 365 | 60.48 | 46.45 | -13.333 | 60.48 | -13.333 |

- Mô hình có mean RMSE thấp nhất trên Test là **Naive persistence** (5.31 m³/s).
- LightGBM D+1 có RMSE 2.79 m³/s, NSE 0.970; D+7 có RMSE 7.10 m³/s, NSE 0.802.
- Năm có RMSE trung bình cao nhất của LightGBM trên Test là 2023 (5.38 m³/s).
- Kết quả chỉ mô tả Test 2022–2023, không phải bảo đảm cho dự báo vận hành hay cảnh báo lũ.
