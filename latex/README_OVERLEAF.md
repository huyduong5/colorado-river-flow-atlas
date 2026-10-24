# Hướng dẫn Overleaf

1. Upload `latex_overleaf.zip` lên Overleaf (New Project → Upload Project).
2. Trong Menu → Compiler, chọn **XeLaTeX**.
3. Đặt `main.tex` làm tệp gốc.
4. Compile 2 lần để cập nhật tham chiếu bảng/hình.
5. Kiểm tra số trang bằng PDF viewer hoặc `pdfinfo main.pdf`; yêu cầu ≤ 5 trang.

## Nội dung gói

- `main.tex`: preamble, bìa, tóm tắt, điều phối section.
- `sections/`: nội dung Q1, Q2, Q3, thảo luận, kết luận, phụ lục, tài liệu tham khảo.
- `tables/`, `figures/`: bảng/hình vector.
- `generated/numbers.tex`: số liệu sinh từ pipeline; không sửa tay.
- `metadata.tex`: thông tin tác giả.
- `assets/logo_dhkhtn.jpg`: logo trường, dùng nhỏ.
- `latexmkrc`: cấu hình XeLaTeX cho latexmk.

## Font

Preamble ưu tiên `Noto Serif`/`Noto Sans`; nếu máy không có, fallback `DejaVu Serif`/
`DejaVu Sans`/`Latin Modern`. Không cần cài font thủ công trên Overleaf.

## Lưu ý

- Không sửa `generated/numbers.tex` bằng tay; chạy lại pipeline `export` nếu dữ liệu đổi.
- Nếu PDF vượt 5 trang, giảm chiều cao hình (giữ nguyên nội dung bắt buộc), không dùng
  font quá nhỏ.
- PDF trong `deliverables/` được tạo bằng Tectonic local; Overleaf có thể cho ngắt dòng
  hơi khác nhưng nội dung và số liệu giữ nguyên.
