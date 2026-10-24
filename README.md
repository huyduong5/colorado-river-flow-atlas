# Colorado River Flow Atlas

Phân tích chuỗi thời gian và dự báo 7 ngày cho lưu lượng sông Colorado, giai đoạn
2010–2023. Đây là bài tập 2 môn Phân tích chuỗi thời gian; PDF tối đa 5 trang là sản
phẩm nộp bắt buộc, website và mã nguồn là hồ sơ bổ sung.

## Sản phẩm

| Sản phẩm | Đường dẫn |
|---|---|
| Báo cáo PDF (bản nộp) | `deliverables/23001524_DUONGQUANGHUY_BAITAP2.pdf` |
| Gói LaTeX cho Overleaf | `deliverables/latex_overleaf.zip` |
| Mã nguồn + kết quả | `deliverables/source_code.zip` |
| Website đã build | `code/web/dist/` |
| Website source | `code/web/` |
| GitHub public | https://github.com/huyduong5/colorado-river-flow-atlas |
| Website public | https://huyduong5.github.io/colorado-river-flow-atlas/ |

## Kết quả chính

- Dữ liệu: 5.113 ngày, 2010-01-01 → 2023-12-31; không thiếu/trùng ngày; SHA256
  `f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660`.
- Q1: mùa vụ yếu (seasonal strength 0,104); trung bình tháng 292,32–300,16 m³/s;
  trung bình năm 129,01 (2010) → 411,57 (2017) m³/s.
- Q2: Q95 = 417,23 m³/s; 256 ngày vượt ngưỡng (5,01%), 15 đợt; đợt dài nhất 90 ngày;
  đỉnh lớn nhất 457,49 m³/s.
- Q3: Test 2022–2023, 724 ngày gốc, 5.068 cặp dự báo. Naive persistence có mean RMSE
  5,31 m³/s; LightGBM direct 7 (delta) 5,33 m³/s; Seasonal Naive 365 60,48 m³/s.
  Naive nhỉnh hơn một chút; kết quả được báo cáo nguyên trạng.

## Cấu trúc

```text
ungdungtuan2/
  plan.md                  # kế hoạch thực hiện
  README.md                # tệp này
  TASKS.md                 # trạng thái công việc
  code/                    # pipeline Python, config, tests, website
  latex/                   # source báo cáo, hình, bảng
  deliverables/            # PDF, ZIP, checksum
```

## Chạy nhanh

```bash
cd code
.venv/bin/python -m pytest -q
.venv/bin/python -m colorado_flow.pipeline --stage all
npm --prefix web test
npm --prefix web run build
```

Nếu chưa có môi trường:

```bash
cd code
uv venv --system-site-packages .venv
uv pip install --python .venv/bin/python -e .
```

`code/.venv` không được đưa vào ZIP source. Các phiên bản đã kiểm tra nằm trong
`code/requirements.lock.txt`.

## Website

Website đọc dữ liệu đã xuất trong `code/web/public/data`. Chạy local:

```bash
cd code/web
npm run dev
```

Build tĩnh:

```bash
cd code/web
npm run build
python3 -m http.server 4173 --directory dist
```

Website có các trang: Tổng quan, Khám phá dữ liệu, Xu hướng & mùa vụ, Cực trị Q95,
Dự báo 7 ngày, So sánh mô hình, Phương pháp, Tải về.

Bản công khai: https://huyduong5.github.io/colorado-river-flow-atlas/

Mã nguồn công khai: https://github.com/huyduong5/colorado-river-flow-atlas

## Báo cáo PDF

PDF hiện tại dài đúng 5 trang, được biên dịch bằng XeLaTeX (Tectonic local). Source
trong `latex/` có thể upload Overleaf; xem `latex/README_OVERLEAF.md`.

## Giới hạn

- Chỉ có 14 năm dữ liệu ngày; Test 2 năm.
- Chưa có biến ngoại sinh (mưa, nhiệt độ, tuyết tan, vận hành hồ chứa).
- GRU chưa chạy vì môi trường không có PyTorch; không có kết quả GRU trong báo cáo.
- Kết quả là backtest, không phải dự báo vận hành hoặc cảnh báo lũ.
