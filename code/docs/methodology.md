# Phương pháp

## 1. Chuỗi thời gian và gốc dự báo

Mỗi ngày gốc `t` tạo 7 dự báo cho `t+1 … t+7`. Một dự báo hợp lệ chỉ dùng dữ liệu đến
hết ngày `t`. Các cửa sổ mục tiêu không vượt khỏi tập tương ứng.

## 2. Chia tập

| Tập | Khoảng | Vai trò |
|---|---|---|
| Train | 2010-01-01 → 2019-12-31 | Huấn luyện ban đầu |
| Validation | 2020-01-01 → 2021-12-31 | Chọn mô hình/siêu tham số |
| Test | 2022-01-01 → 2023-12-31 | Báo cáo một lần |
| Refit | 2010-01-01 → 2021-12-31 | Huấn luyện lại sau khi chọn |

Số ngày gốc: 3.615 Train, 725 Validation, 724 Test, 4.346 Refit. Không xáo trộn.

## 3. Feature

- Lag 1, 2, 3, 7, 14, 21, 28, 30 ngày.
- Trung bình và độ lệch chuẩn trượt 7, 14, 30 ngày.
- Sin/cos của ngày trong năm và tháng tại ngày gốc.
- Sin/cos lịch của ngày mục tiêu cho từng horizon.
- Không dùng giá trị tương lai, không dùng target trong feature.

## 4. Mô hình

### Naive persistence

`ŷ(t+h) = y(t)`.

### Seasonal Naive 365

`ŷ(t+h) = y(t+h-365)`.

### LightGBM direct 7 (delta)

Mỗi horizon có một model riêng. Mục tiêu là `q(t+h) - q(t)`, dự báo cuối cùng là
`q(t) + Δ̂`. Cách này giữ vai trò persistence trong mô hình và ổn định hơn khi mức nền
thay đổi. Siêu tham số tìm trên Validation; early stopping dùng Validation, không dùng
Test.

## 5. Chỉ số

```text
RMSE = sqrt(mean((y - ŷ)^2))
MAE  = mean(|y - ŷ|)
NSE  = 1 - sum((y - ŷ)^2) / sum((y - mean(y))^2)
```

`mean_*` lấy trung bình trên 7 horizon; `pooled_*` tính trên toàn bộ cặp. NSE = 1 là
hoàn hảo, NSE = 0 tương đương dự báo bằng trung bình, NSE < 0 là kém hơn trung bình.

## 6. Q95 và cực trị

Q95 tính bằng quantile tuyến tính trên toàn bộ chuỗi 2010–2023, không tính lại theo
năm. Các ngày có `q > Q95` được gộp thành đợt nếu liên tiếp theo ngày lịch. Z tương
đương là `(Q95 - mean) / std_sample`; với dữ liệu này xấp xỉ 1,224, không phải 1,645.

## 7. Diễn giải

Mùa vụ yếu, trend mạnh và chuỗi gần random-walk ở tần suất ngày. Vì vậy baseline
persistence là đối thủ mạnh; LightGBM không được kỳ vọng thắng đậm. Kết quả Test được
báo cáo nguyên trạng.
