# Nhật ký thực nghiệm

## Run hiện tại

- Run ID: `run-20261024T160504+0000`
- Dataset SHA256: `f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660`
- Seed: 42
- Horizon: 7; split theo thời gian.

## Lựa chọn LightGBM

- Target mode: `delta` (`q(t+h) - q(t)`).
- 8 trial trên Validation; best trial 8.
- Best params: `learning_rate=0.05`, `num_leaves=7`, `max_depth=3`,
  `min_child_samples=40`, `reg_lambda=0.0`.
- Early stopping 50 vòng; best iteration rất nhỏ ở một số horizon (D+2 = 1), cho thấy
  mô hình gần persistence.

## Validation

| Mô hình | Mean RMSE | Mean MAE | Mean NSE |
|---|---:|---:|---:|
| Naive persistence | 5,535150 | 4,424238 | 0,987592 |
| LightGBM delta | 5,570257 | 4,441528 | 0,987417 |
| Seasonal Naive 365 | 65,5717 | — | — |

## Test 2022–2023

724 ngày gốc, 5.068 cặp mỗi mô hình.

| Mô hình | Mean RMSE | Mean MAE | Mean NSE | Pooled RMSE | Pooled NSE |
|---|---:|---:|---:|---:|---:|
| Naive persistence | 5,307564 | 4,155260 | 0,881416 | 5,496230 | 0,881647 |
| LightGBM direct 7 (delta) | 5,325013 | 4,168852 | 0,880502 | 5,517349 | 0,880735 |
| Seasonal Naive 365 | 60,484006 | 46,446319 | -13,332921 | 60,484362 | -13,333008 |

## Nhận xét

- LightGBM chỉ nhỉnh hơn Naive ở D+1; từ D+2 đến D+7 Naive tốt hơn.
- Không tinh chỉnh trên Test.
- Seasonal Naive 365 thất bại vì mùa vụ yếu.
- GRU chưa chạy; không có kết quả GRU.
