# QA checklist

| Kiểm tra | Trạng thái | Bằng chứng |
|---|---|---|
| 5.113 ngày, đúng lịch, không thiếu/trùng | Đạt | `pytest`; `data_quality.json` |
| SHA256 khớp | Đạt | `test_data_contract.py` |
| Q95 = 417,230854; 256 ngày; 15 đợt | Đạt | `q2_summary.json` |
| Split 3.615 / 725 / 724 / 4.346 | Đạt | `split_manifest.json` |
| Không rò rỉ feature | Đạt | `test_features_no_leakage.py` |
| Test đủ 5.068 cặp mỗi mô hình | Đạt | `predictions_long.csv` |
| Metrics khớp PDF/website/CSV | Đạt | test export + kiểm tra thủ công |
| Python tests | Đạt | 14 passed |
| Clean venv + full pipeline | Đạt | venv mới cài từ `requirements.lock.txt`; 14 test pass; pipeline tái tạo đúng metrics/predictions của run cuối |
| Web smoke test | Đạt | `npm test`: manifest/schema, 5.113 ngày, 15 đợt, 5.068 cặp/3 model, file tải |
| Web typecheck/build | Đạt | `tsc --noEmit`, `vite build` |
| Runtime JSON schema | Đạt | `web/src/lib/api.ts` kiểm tra manifest/daily/metrics/extremes/predictions |
| Chart zoom/restore/PNG | Đạt | ECharts toolbox; forecast có slider 60 ngày + 7 ngày |
| Responsive 375/768/1440 | Đạt | `screenshots/mobile-375.png`, `tablet-768.png`, `desktop-1440.png`; `scrollWidth <= innerWidth` (chênh lệch chỉ do scrollbar dọc) |
| Không tràn ngang toàn trang | Đạt | CDP: 375/768/1440 đều không overflow; nav mobile cuộn trong khung |
| PDF ≤ 5 trang | Đạt | `pdfinfo` = 5 |
| PDF có figure/table tiếng Việt | Đạt | render 5 trang |
| PDF có Phụ lục B hồ sơ số | Đạt | trang 5; vẫn đúng 5 trang |
| Overleaf source đủ | Đạt | `latex_overleaf.zip` |
| Source ZIP không chứa `.venv`/`node_modules` | Đạt | script đóng gói |
| Không có URL website giả | Đạt | chỉ link local/PDF |
| GRU | N/A | Không có PyTorch; ghi rõ trong báo cáo |
| Website publish công khai | Chưa | chỉ build local + hướng dẫn |

## Ghi chú

- Ảnh render website nằm trong `docs/screenshots/` (overview, seasonality, forecast,
  models, methods, downloads, mobile-375, tablet-768, desktop-1440).
- Wireframe và luồng sử dụng: `docs/wireframes.md`.
- Nếu chạy lại pipeline, phải chạy lại `evaluate`, `export`, build web và PDF để giữ
  cùng `run_id`.
