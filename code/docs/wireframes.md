# Wireframe và luồng sử dụng

Ảnh prototype thật nằm trong `screenshots/`. File này mô tả cấu trúc trước khi dựng
giao diện, dùng cho Gate G8.

## Desktop ≥ 1100 px

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [CR] Colorado River Flow Atlas            01/01/2010–31/12/2023  [PDF báo cáo]│
├───────────────┬──────────────────────────────────────────────────────────────┤
│ NỘI DUNG      │ KICKER · Q                                                       │
│ 00 Tổng quan  │ Tiêu đề trang                                                    │
│ 01 Khám phá   │ Một đoạn dẫn có số liệu                                          │
│ 02 Mùa vụ     │ [KPI] [KPI] [KPI] [KPI]                                          │
│ 03 Cực trị    │ ┌────────────────────────────────────────────────────────────┐   │
│ 04 Dự báo     │ │ ChartPanel: tiêu đề, mô tả, toolbar zoom/restore/PNG      │   │
│ 05 Mô hình    │ │                                                            │   │
│ 06 Phương pháp│ └────────────────────────────────────────────────────────────┘   │
│ 07 Tải về     │ ┌───────────────────┐ ┌──────────────────────────────────┐     │
│               │ │ Bảng / callout    │ │ Chart hoặc bảng phụ              │     │
│ [PHẠM VI]     │ └───────────────────┘ └──────────────────────────────────┘     │
│ run_id        │ Kết luận ngắn · nguồn · giới hạn                                 │
└───────────────┴──────────────────────────────────────────────────────────────┘
```

## Mobile ≤ 620 px

```text
┌──────────────────────────┐
│ [CR] Atlas               │
│ PDF báo cáo              │
├──────────────────────────┤
│ Tổng quan · Khám phá →   │  nav cuộn ngang, tab active có gạch chân
├──────────────────────────┤
│ KICKER                   │
│ Tiêu đề lớn, xuống dòng  │
│ Đoạn dẫn                 │
│ [CTA] [CTA]              │
│ ┌──────────────────────┐ │
│ │ KPI                   │ │
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ Chart + toolbar       │ │
│ └──────────────────────┘ │
│ Bảng cuộn trong panel    │
└──────────────────────────┘
```

## Luồng chính

1. Tổng quan → xem 4 KPI, hydrograph, chọn Q1/Q2/Q3.
2. Khám phá → chọn khoảng ngày → xem KPI/chart → tải CSV đúng khoảng.
3. Mùa vụ → boxplot tháng, trung bình năm, heatmap năm × tháng; so sánh biên độ.
4. Cực trị → xem toàn chuỗi + Q95 → chọn một đợt trong bảng → biểu đồ zoom đúng đợt.
5. Dự báo → chọn model và ngày gốc → xem 60 ngày lịch sử + 7 ngày dự báo → bật/tắt
   giá trị thực tế → xem bảng D+1…D+7 và sai số.
6. Mô hình → xem RMSE/MAE/NSE theo horizon/năm → sang Dự báo hoặc Phương pháp.
7. Phương pháp → đọc split, feature, metric, giới hạn.
8. Tải về → tải PDF, source ZIP, LaTeX ZIP, CSV; đối chiếu checksum và run_id.

## Trạng thái lỗi

- JSON sai schema: `api.ts` ném lỗi có tên tệp và trường; App hiện màn hình “Không tải
  được Atlas” kèm nút thử lại.
- Ngày không hợp lệ: trang Khám phá kẹp về min/max; trang Dự báo chỉ cho chọn origin có
  trong manifest.
- Bảng rỗng: hiện “Không có dữ liệu.” thay vì bảng trắng.
- Không có backend/API ngoài; toàn bộ dữ liệu đọc từ `public/data`.
