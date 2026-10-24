# Hướng dẫn Overleaf — báo cáo đầy đủ

1. Nén thư mục `latex_full/` (hoặc dùng `deliverables/latex_full_overleaf.zip` khi có)
   rồi upload lên Overleaf: **New Project → Upload Project**.
2. Trong **Menu → Compiler**, chọn **XeLaTeX**.
3. Đặt `main.tex` làm tệp gốc.
4. Compile **2 lần** để cập nhật mục lục, danh mục bảng/hình và tham chiếu chéo.
5. Kiểm tra `pdfinfo main.pdf`: bản hiện tại có **41 trang** (mục tiêu 40–45 trang).

## Nội dung gói

- `main.tex`: preamble, bìa, đánh số La Mã/Ả Rập và điều phối section.
- `sections/`: tóm tắt, dữ liệu, kiểm tra chất lượng, Q1, Q2, Q3, website,
  thảo luận, kết luận, tài liệu tham khảo và phụ lục.
- `tables/`: 14 bảng sinh tự động.
- `figures/`: 14 hình PDF sinh tự động.
- `generated/numbers.tex`: số liệu, tham số và metric do pipeline sinh.
- `generated/assets_manifest.json`: manifest run ID, bảng, hình và tệp đi kèm.
- `assets/`: logo, QR và ảnh chụp website.
- `metadata.tex`: thông tin tác giả.

## Font

Preamble ưu tiên `Noto Serif`/`Noto Sans`/`Noto Sans Mono`; nếu thiếu thì fallback
`DejaVu` rồi `Latin Modern`. Không cần cài font thủ công trên Overleaf.

## Lưu ý

- Không sửa tay `generated/numbers.tex`, `tables/` hoặc `figures/`; chạy lại
  `python -m colorado_flow.pipeline --stage export` nếu dữ liệu thay đổi.
- Không cần `--shell-escape`; báo cáo chỉ dùng hình PDF/PNG và không gọi lệnh hệ thống.
- Có thể còn cảnh báo `Overfull \hbox` rất nhỏ ở phần bìa/phụ lục; không ảnh hưởng nội dung.
- Bản PDF local được biên dịch bằng Tectonic (XeLaTeX). Overleaf có thể ngắt dòng hơi
  khác nhưng số liệu, bảng, hình và thứ tự section được giữ nguyên.
- Bản 5 trang dự phòng nằm trong `latex/` và `deliverables/`; không trộn hai bộ source.
