# Kế hoạch thực hiện Bài tập 2 về lưu lượng sông Colorado

> Tài liệu kế hoạch triển khai dự án. Ngày lập: 24/10/2026; cập nhật: 24/10/2026.
> Mục tiêu: PDF nộp bài tối đa 5 trang là sản phẩm bắt buộc; website, bộ LaTeX Overleaf và mã nguồn là hồ sơ bổ sung của dự án.
> Tài liệu này là kế hoạch thực hiện, chưa phải báo cáo kết quả huấn luyện. Các số liệu kiểm tra ban đầu dưới đây đã được tính trực tiếp từ CSV; mọi chỉ số dự báo phải được sinh sau khi chạy thực nghiệm.

## 1. Chỉ dẫn bắt đầu

1. Đọc toàn bộ kế hoạch, sau đó mở bốn tệp tài liệu đầu vào trong thư mục dự án hiện tại và đối chiếu checksum CSV ở mục 3.
2. Gốc dự án là thư mục hiện tại `ungdungtuan2/`; tạo `code/`, `latex/` và `deliverables/` ngay tại đây theo mục 6, không lồng thêm thư mục `colorado-river-atlas/`.
3. Triển khai lần lượt các phase; không bỏ qua bước khóa giao thức dự báo và kiểm tra rò rỉ dữ liệu.
4. Mỗi task hoàn tất phải có sản phẩm thực tế và bằng chứng nghiệm thu. Cập nhật trạng thái trong `TASKS.md`, không chỉ ghi nhận bằng lời.
5. Phần phân tích, website và báo cáo phải dùng chung nguồn kết quả. Không gõ lại các chỉ số bằng tay ở nhiều nơi.
6. Hoàn thành bản chạy được với baseline và LightGBM trước, sau đó thêm GRU, kiểm định kết quả, hoàn thiện website và PDF.
7. Không yêu cầu người dùng chọn lại các quyết định kỹ thuật đã quy định ở đây. Tự giải quyết các lựa chọn thường lệ và ghi lý do nếu cần thay đổi.
8. Không tạo số liệu, URL website công khai, nguồn dữ liệu trạm, cấu hình máy chủ hoặc kết quả training khi chưa kiểm chứng.
9. Nếu thiếu thời gian, hoàn thành trước Q1, Q2, Q3 với Naive + LightGBM và PDF 5 trang; GRU, website, LaTeX và source là các phần mở rộng được ưu tiên sau.

### 1.1. File đầu vào

| Tệp | Đường dẫn tương đối | Vai trò |
|---|---|---|
| `Yêu cầu BÀI TẬP 2.docx` | `./Yêu cầu BÀI TẬP 2.docx` | Nguồn yêu cầu chính thức, ưu tiên cao nhất |
| `colorado_river_flow.csv` | `./colorado_river_flow.csv` | Dataset duy nhất dùng trong thực nghiệm chính |
| `23001524_DUONGQUANGHUY_BAITAP1.pdf` | `./23001524_DUONGQUANGHUY_BAITAP1.pdf` | Danh tính, phong cách báo cáo, cách kết nối website với phân tích |
| `Tham khao mau bao cao bai tap 1.pdf` | `./Tham khao mau bao cao bai tap 1.pdf` | Mẫu diễn giải học thuật, bảng, hình và nhận xét |
| `logo_dhkhtn.jpg` | `./logo_dhkhtn.jpg` | Logo trường dùng tùy chọn trên bìa; ảnh gốc 89×108 px |

Tên tệp chính xác dùng làm căn cứ là `23001524_DUONGQUANGHUY_BAITAP1.pdf`. Giữ nguyên bốn tệp tài liệu đầu vào và logo ở gốc dự án; chỉ đọc, không sửa. Khi triển khai, copy CSV sang `code/data/raw/colorado_river_flow.csv` và đối chiếu SHA256.

### 1.2. Thông tin tác giả lấy từ báo cáo bài 1

| Trường | Giá trị dùng trong dự án |
|---|---|
| Trường | Trường Đại học Khoa học Tự nhiên |
| Khoa | Toán Cơ - Tin học; giữ cách ghi trên báo cáo gốc hoặc chuẩn hóa dấu nối nhất quán |
| Họ và tên | Dương Quang Huy |
| Ngành | Khoa học dữ liệu |
| Khóa | 68 |
| Giáo viên hướng dẫn | GS. Đỗ Minh Đức |
| Địa điểm, năm | Hà Nội, 2026 |
| Mã sinh viên | `23001524`, suy từ tên file; bìa trích xuất được không có dòng MSSV, cần đối chiếu nếu thêm lên bìa |
| Tiêu đề mới | PHÂN TÍCH VÀ DỰ BÁO CHUỖI THỜI GIAN LƯU LƯỢNG DÒNG CHẢY SÔNG COLORADO GIAI ĐOẠN 2010–2023 |

Không mang tiêu đề mưa Trà My, thời đoạn 2008–2017 hay kết luận của bài 1 sang bài 2.

## 2. Phân tích đề và các quyết định bắt buộc

### 2.1. Ma trận yêu cầu và bằng chứng

Đề không đánh số từng câu; dùng Q1–Q3 dưới đây để quản lý, không diễn đạt như thể đây là số câu có sẵn trong DOCX. Q4 là ràng buộc nộp bài. U1–U3 là yêu cầu bổ sung của dự án, không có trong DOCX, nên không được làm chậm Q1–Q3.

| Mã | Yêu cầu từ đề | Công việc bắt buộc | Bằng chứng nghiệm thu |
|---|---|---|---|
| Q1 | Phân tích Trend, Seasonality; nhận xét chu kỳ hàng năm | Chuỗi gốc, xu hướng, chu trình tháng, kiểm tra mùa vụ sau tách xu hướng | Hình, bảng tháng/năm, nhận xét có số liệu |
| Q2 | Toàn chuỗi 2010–2023; Z-score tĩnh hoặc moving; highlight Top 5% | Hydrograph đầy đủ, Q95, Z-score, các ngày vượt ngưỡng và nhóm đợt | Hình toàn chuỗi, bảng sự kiện, công thức và định nghĩa ngưỡng |
| Q3a | Train/Validation 2010–2021; Test 2022–2023; không xáo trộn | Tách theo thời gian và kiểm tra toàn bộ nhãn dự báo | `split_manifest.json`, test tự động |
| Q3b | Baseline | Naive persistence (bắt buộc); Seasonal Naive là mở rộng để đối chiếu | Dự báo 7 bước và bảng chỉ số |
| Q3c | Dự báo 7 ngày bằng LSTM/GRU hoặc XGBoost/LightGBM | LightGBM direct 7 horizon (hướng chính, đáp ứng đề); GRU direct 7 đầu ra là mở rộng nếu đủ thời gian | Model, config, lịch sử train, dự báo từng horizon |
| Q3d | RMSE, MAE, NSE trên Test | Theo từng D+1…D+7 và tổng hợp có định nghĩa | CSV/JSON chỉ số và bảng báo cáo |
| Q4 | PDF tối đa 5 trang | Bố cục 5 trang gồm cả bìa và tài liệu tham khảo | PDF đã đếm trang và kiểm tra trực quan |
| U1 | Website dễ nhìn, dễ dùng, trực quan (bổ sung) | Tra cứu, mùa vụ, cực trị, dự báo, so sánh, phương pháp, tải dữ liệu | Website build được và kiểm thử luồng sử dụng |
| U2 | Folder LaTeX upload Overleaf (bổ sung) | `main.tex`, section, hình, bảng, tài liệu tham khảo, hướng dẫn | ZIP LaTeX độc lập, biên dịch thành công |
| U3 | Folder mã nguồn đầy đủ (bổ sung) | Pipeline Python, website, config, tests, README | Chạy lại từ checkout sạch với lệnh được tài liệu hóa |

Mức tối thiểu để đạt đề: Q1, Q2, Q3a–Q3d và PDF ≤ 5 trang, với ít nhất một trong hai họ mô hình LightGBM hoặc GRU. Kế hoạch chọn LightGBM làm mô hình chính và giữ GRU như so sánh mở rộng; Seasonal Naive và Moving Z-score cũng là phần bổ sung.

### 2.2. Cách áp dụng báo cáo mẫu

- Giữ tinh thần: bìa trang trọng, đề mục đánh số, dữ liệu và công cụ trước kết quả, công thức ngắn, bảng/hình có số và nhận xét định lượng ngay sau đó.
- Học từ bài 1 của Huy: đưa website thành sản phẩm tra cứu bổ trợ; giải thích phương pháp; minh bạch chất lượng dữ liệu và hạn chế.
- Không sao chép độ dài: bài 1 của Huy có 37 trang, mẫu tham khảo có 14 trang, trong khi bài 2 chỉ được tối đa 5 trang.
- Không làm trang mục lục, trang đề bài riêng hoặc phụ lục ngoài 5 trang. Tóm tắt yêu cầu trong phần mở đầu; chuyển bảng đầy đủ, hình phụ và log sang website/mã nguồn.
- Không kế thừa sai sót của mẫu: số mẫu ở bảng chất lượng và bảng thống kê trong mẫu Lào Cai có chỗ không nhất quán; bài mới phải sinh mọi bảng từ cùng dữ liệu đã kiểm tra.
- Thống kê dòng chảy trung bình tháng/năm dùng **trung bình**, không cộng các giá trị m³/s rồi gọi là lưu lượng tháng/năm. Nếu tính thể tích, phải nhân thời gian 86.400 giây/ngày và đổi đơn vị rõ ràng; phần này không bắt buộc.

## 3. Kết quả kiểm tra CSV ban đầu

Các giá trị dưới đây là mốc kiểm tra đầu vào, không phải chỉ số đánh giá mô hình.

| Hạng mục | Giá trị đã kiểm tra |
|---|---|
| Kích thước | 5.113 dòng, 2 cột |
| Schema | `date`, `discharge_m3s` |
| Khoảng thời gian | 01/01/2010–31/12/2023 |
| Tần suất | Hằng ngày, lịch liên tục |
| Thiếu ngày / ngày trùng | 0 / 0 |
| Ô thiếu / giá trị lưu lượng không hữu hạn / âm | 0 / 0 / 0 |
| Sắp xếp ngày tăng dần | Có |
| Trung bình | 295,683902 m³/s |
| Độ lệch chuẩn mẫu, `ddof=1` | 99,315139 m³/s |
| Nhỏ nhất | 94,390919 m³/s, ngày 23/01/2012 |
| Lớn nhất | 457,485984 m³/s, ngày 10/03/2020 |
| Q95 toàn chuỗi, nội suy tuyến tính | 417,230854 m³/s |
| Số ngày `q > Q95` | 256 ngày, khoảng 5,0068% |
| Ngưỡng Z tương đương Q95, dùng độ lệch chuẩn mẫu | Khoảng 1,223851 |
| 2010–2019 | 3.652 ngày |
| 2020–2021 | 731 ngày |
| 2010–2021 | 4.383 ngày |
| 2022–2023 | 730 ngày |
| SHA256 CSV | `f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660` |

Toàn bộ mốc trong bảng đã được tính lại trực tiếp từ CSV ngày 24/10/2026. Q95 dùng nội suy tuyến tính và điều kiện `q > Q95`, cho đúng 256 ngày (5,0068%); nếu dùng `>=` thì số ngày sẽ khác và không được trộn với định nghĩa này.

### 3.1. Hai lưu ý chuyên môn từ kiểm tra ban đầu

1. Trung bình theo tháng trên toàn bộ 14 năm chỉ dao động khoảng 292,32–300,16 m³/s. Trung bình năm thay đổi lớn: khoảng 129,01 năm 2010, 411,57 năm 2017, 213,61 năm 2023. Đây là dấu hiệu cần phân biệt biến thiên nhiều năm với mùa vụ; chưa đủ căn cứ kết luận mùa vụ không tồn tại. Kiểm tra chuỗi đã tách xu hướng và độ ổn định theo từng năm trước khi nhận xét.
2. Theo đề, đây là dòng chảy tại trạm thực tế trên sông Colorado. Tuy nhiên CSV không có mã trạm, tọa độ, phương pháp đo hoặc cơ quan cung cấp. Báo cáo ghi “dữ liệu được cung cấp trong đề bài”; không tự gán USGS, tên trạm, hồ chứa hoặc nguyên nhân vật lý. Nguồn USGS/NOAA ở mục 5 chỉ là tham khảo thiết kế và phương pháp trình bày, không chứng minh xuất xứ CSV.

Các con số mô tả toàn chuỗi phục vụ Q1/Q2. Mọi lựa chọn đặc trưng, kiến trúc và tham số dự báo phải được quyết định bằng 2010–2021; không dùng quan sát Test để điều chỉnh mô hình.

## 4. Phạm vi và kiến trúc được chọn

### 4.1. Sản phẩm cuối

- Báo cáo `23001524_DUONGQUANGHUY_BAITAP2.pdf`, tối đa 5 trang: sản phẩm bắt buộc để nộp.
- Website “Colorado River Flow Atlas”, nội dung chính bằng tiếng Việt, chạy được trên desktop và điện thoại: hồ sơ bổ sung.
- Pipeline Python có thể chạy lại audit → EDA → features → train → evaluate → export: hồ sơ bổ sung.
- Mô hình tối thiểu đáp ứng đề: Naive persistence + LightGBM direct 7 horizon.
- Mô hình mở rộng: Seasonal Naive và GRU direct 7 đầu ra; chạy nếu đủ thời gian và tài nguyên.
- `latex_overleaf.zip`, đủ source và asset để upload Overleaf: hồ sơ bổ sung.
- `source_code.zip`, gồm mã nguồn phân tích/website/config/tests/hướng dẫn; kèm tập kết quả cần thiết để xem website mà không phải train lại.
- `submission.zip`, gói tùy chọn chứa PDF, hai gói trên và hướng dẫn ngắn; chỉ tạo nếu giảng viên hoặc quy trình nộp yêu cầu.

Baseline + LightGBM đã đáp ứng yêu cầu thuật toán của đề. GRU là hạng mục mở rộng để có so sánh giữa hai họ mô hình; nếu không thực hiện được vì hạn chế môi trường, phải ghi minh bạch trong bàn giao, không tạo hàng kết quả giả. Không thêm Transformer, Mamba, mô hình khí tượng đa nguồn hay tối ưu siêu tham số quy mô lớn vào phạm vi chính.

### 4.2. Công nghệ

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| Phân tích | Python, pandas, NumPy, SciPy, statsmodels | Đủ cho kiểm tra chuỗi, phân rã và thống kê |
| Machine learning | LightGBM, scikit-learn | Phù hợp dataset nhỏ, chạy CPU tốt |
| Deep learning | PyTorch GRU | Kiến trúc nhỏ, dự báo vector 7 ngày |
| Hình báo cáo | Matplotlib, xuất PDF vector và PNG 300 dpi | In rõ và thống nhất kiểu chữ |
| Website | React + TypeScript + Vite | Cấu trúc dễ bảo trì, build tĩnh, không cần server inference |
| Biểu đồ | Apache ECharts | Zoom, tooltip, highlight, heatmap, xuất ảnh |
| Style | CSS có design tokens | Giao diện gọn, ít phụ thuộc |
| Báo cáo | XeLaTeX, font TeX Gyre Termes, hỗ trợ tiếng Việt | Gần phong cách Times của mẫu, chạy trên Overleaf |
| Kiểm thử | pytest; Playwright hoặc trình kiểm thử browser tương đương | Kiểm tra tính đúng số liệu và luồng website |
| Triển khai | Build tĩnh; ưu tiên GitHub Pages nếu có repo/quyền sẵn | Không buộc phải duy trì máy chủ để phục vụ website liên tục |

Chọn phiên bản ổn định và khóa phiên bản thực tế khi triển khai bằng lockfile. Không ghi “latest” trong môi trường cần tái lập.

#### 4.2.1. Môi trường đã kiểm tra ngày 24/10/2026

| Thành phần | Trạng thái trên máy hiện tại |
|---|---|
| Python | 3.12.3 |
| Node / npm | 22.18.0 / 10.9.3 |
| Thư viện Python đã có | numpy, pandas, scipy, scikit-learn, matplotlib, pytest, pyyaml |
| Thư viện còn thiếu | statsmodels, lightgbm, torch |
| LaTeX | Chưa có `xelatex` và `latexmk`; dùng Overleaf hoặc cài TeX Live nếu cần biên dịch local |
| Tài nguyên | Khoảng 1,2 GiB RAM khả dụng, khoảng 4,7 GB ổ đĩa trống |

Lệnh cài tối thiểu cho phân tích và LightGBM (chạy trong `code/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas numpy scipy statsmodels scikit-learn lightgbm matplotlib pyyaml pytest
```

Chỉ cài PyTorch bản CPU nếu thực hiện GRU; không cài gói CUDA trên máy này. Nếu không cài được TeX Live do hạn chế dung lượng, biên dịch trực tiếp trên Overleaf và kiểm tra ZIP bằng một lần upload thử. LightGBM và GRU nhỏ chạy CPU là đủ cho dataset 5.113 ngày; không cần GPU.

### 4.3. Luồng kết quả

`CSV gốc → kiểm tra dữ liệu → xử lý theo giao thức thời gian → phân tích/huấn luyện → dự báo và chỉ số → bộ kết quả chuẩn → website + bảng/hình LaTeX → PDF`.

Website chỉ đọc JSON/CSV đã xuất, không train trong trình duyệt. Với 5.113 ngày và số lượng dự báo nhỏ, không cần database, backend, đăng nhập hoặc GPU phục vụ người xem.

## 5. Tham khảo website và tài liệu đã khảo sát

Khảo sát nguồn chính thức ngày 24/10/2026. Dùng các liên kết dưới đây trong `code/docs/design-references.md`, ghi rõ phần học hỏi và phần tự thiết kế.

| Nguồn | URL | Điểm vận dụng |
|---|---|---|
| USGS Water Data for the Nation | https://waterdata.usgs.gov/ | Tổ chức tra cứu dữ liệu, biểu đồ và đường dẫn tải xuống |
| USGS Explore Water Data | https://waterdata.usgs.gov/explore/ | Bộ lọc và luồng khám phá dữ liệu lịch sử |
| USGS giới thiệu giao diện dữ liệu | https://waterdata.usgs.gov/blog/wdfn-updates-2025/ | Kết nối graphs, tables và ngữ cảnh thống kê |
| NOAA National Water Prediction Service | https://water.noaa.gov/ | Tham khảo sản phẩm quan trắc/dự báo thủy văn |
| NOAA giới thiệu NWPS | https://www.noaa.gov/news-release/national-weather-service-launches-new-website-for-water-prediction-and-products | Ý tưởng phân biệt đoạn quan trắc và đoạn dự báo trên hydrograph |
| Apache ECharts gallery | https://echarts.apache.org/examples/en/index.html | Line/area, boxplot, heatmap, tương tác zoom; phải chạy thử trong browser khi triển khai |
| scikit-learn TimeSeriesSplit | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html | Kiểm chứng chia tập theo thời gian và ý nghĩa gap |
| statsmodels STL | https://www.statsmodels.org/stable/examples/notebooks/generated/stl_decomposition.html | Cơ sở triển khai phân rã xu hướng và mùa vụ |
| LightGBM parameters | https://lightgbm.readthedocs.io/en/stable/Parameters.html | Chọn và ghi cấu hình mô hình |
| PyTorch GRU | https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html | Kiểm tra shape và tham số GRU theo bản cài |
| Nash và Sutcliffe, 1970 | https://www.sciencedirect.com/science/article/pii/0022169470902556 | Tài liệu gốc cho NSE, DOI `10.1016/0022-1694(70)90255-6` |

Phạm vi khảo sát hiện tại: đã đọc nội dung công khai của USGS và bài giới thiệu NOAA; URL dashboard USGS trả về 403 khi truy xuất trực tiếp, gallery ECharts yêu cầu JavaScript. Khi triển khai, cần mở được gallery/browser hoặc tham khảo tài liệu công khai tương đương để chốt chi tiết tương tác.

Không sao chép giao diện, logo hay tên sản phẩm của các cơ quan. Không dựng bản đồ trạm giả khi CSV không có tọa độ. Biểu đồ là trọng tâm; hình ảnh minh họa sông chỉ là tùy chọn và không được lấn át dữ liệu.

## 6. Cấu trúc thư mục cần tạo

Gốc dự án: thư mục hiện tại `ungdungtuan2/` (trên máy này là `/home/yue/Downloads/ungdungtuan2/`). Sử dụng Markdown code block để mô tả đường dẫn, không tạo thư mục trống thay cho triển khai thực tế.

```text
ungdungtuan2/
  plan.md
  README.md
  TASKS.md
  Yêu cầu BÀI TẬP 2.docx
  colorado_river_flow.csv
  23001524_DUONGQUANGHUY_BAITAP1.pdf
  Tham khao mau bao cao bai tap 1.pdf
  logo_dhkhtn.jpg
  code/
    README.md
    pyproject.toml
    requirements.lock.txt
    .gitignore
    configs/
      default.yaml
      lightgbm.yaml
      gru.yaml
    data/
      raw/colorado_river_flow.csv
      interim/
      processed/
    src/colorado_flow/
      __init__.py
      pipeline.py
      io.py
      audit.py
      descriptive.py
      seasonality.py
      extremes.py
      splits.py
      features.py
      datasets.py
      metrics.py
      evaluation.py
      export_web.py
      export_latex.py
      provenance.py
      models/
        __init__.py
        naive.py
        seasonal_naive.py
        lightgbm_direct.py
        gru.py
    notebooks/
      01_data_audit.ipynb
      02_trend_seasonality.ipynb
      03_forecast_diagnostics.ipynb
    tests/
      test_data_contract.py
      test_temporal_splits.py
      test_features_no_leakage.py
      test_metrics.py
      test_forecast_protocol.py
      test_export_consistency.py
    scripts/
      run_pipeline.sh
      train.sh
      collect_results.sh
      build_submission.sh
    results/
      run_manifest.json
      data_quality.json
      split_manifest.json
      model_selection.json
      metrics_overall.csv
      metrics_by_horizon.csv
      metrics_by_year.csv
      predictions_long.csv
      extreme_events.csv
      tables/
      figures/
      checkpoints/
      logs/
    web/
      package.json
      package-lock.json
      vite.config.ts
      tsconfig.json
      index.html
      public/
        data/
        downloads/
      src/
        main.tsx
        App.tsx
        styles/
        types/
        lib/
        components/
          AppShell.tsx
          DateRangeFilter.tsx
          StatCard.tsx
          ChartPanel.tsx
          DataTable.tsx
          MethodNote.tsx
          ExportButton.tsx
        pages/
          OverviewPage.tsx
          ExplorePage.tsx
          SeasonalityPage.tsx
          ExtremesPage.tsx
          ForecastPage.tsx
          ModelsPage.tsx
          MethodsPage.tsx
          DownloadsPage.tsx
      tests/
    docs/
      requirements.md
      data_dictionary.md
      methodology.md
      design-references.md
      experiment_log.md
      findings.md
      reproducibility.md
      qa_checklist.md
      screenshots/
  latex/
    README_OVERLEAF.md
    main.tex
    preamble.tex
    metadata.tex
    latexmkrc
    references.bib
    sections/
      00_cover.tex
      01_data_trend.tex
      02_extremes_protocol.tex
      03_model_results.tex
      04_discussion_conclusion.tex
    figures/
    tables/
    generated/
      numbers.tex
    assets/
      logo_dhkhtn.jpg
  deliverables/
    23001524_DUONGQUANGHUY_BAITAP2.pdf
    latex_overleaf.zip
    source_code.zip
    submission.zip
```

`latex/assets/logo_dhkhtn.jpg` là bản copy từ `./logo_dhkhtn.jpg`; ảnh gốc chỉ 89×108 px nên chỉ dùng ở kích thước nhỏ khoảng 1,2–1,5 cm hoặc bỏ nếu in mờ. Không kéo giãn, không dùng logo khác không có nguồn. Thiếu logo không được làm hỏng biên dịch. Các file kết quả trong cây chỉ xuất hiện sau khi pipeline tương ứng chạy xong. Bốn tệp tài liệu đầu vào và logo gốc ở root chỉ đọc; `code/data/raw/colorado_river_flow.csv` là bản copy bất biến dùng cho pipeline. `submission.zip` là tùy chọn, chỉ tạo nếu quy trình nộp yêu cầu.

## 7. Quy ước khoa học cần khóa trước khi train

### 7.1. Định nghĩa gốc dự báo

- Ký hiệu `t` là ngày cuối cùng đã biết quan trắc `q_t`.
- Input tại gốc `t` chỉ chứa giá trị có ngày `≤ t` và thông tin lịch biết trước.
- Output là vector `[q_(t+1), …, q_(t+7)]`.
- GRU nhận cửa sổ `L` ngày `[q_(t-L+1), …, q_t]`, shape `[batch, L, features]`, xuất `[batch, 7]`.
- LightGBM dùng 7 mô hình độc lập, mô hình thứ `h` dự báo `q_(t+h)` từ đặc trưng tại cùng gốc `t`; không sử dụng giá trị thật của D+1 để dự báo D+2 trong cùng lần phát hành.
- Đánh giá chính là rolling-origin: mô hình đã khóa trọng số, mỗi ngày có thể cập nhật lịch sử bằng quan trắc vừa có, rồi phát hành 7 dự báo mới. Đây không phải dự báo một lần từ cuối 2021 cho toàn bộ hai năm.
- Lưu cả `origin_date`, `target_date`, `horizon` và `model` để không nhầm nhiều dự báo cho cùng ngày.

### 7.2. Tách Train, Validation và Test

| Giai đoạn | Ngày mục tiêu được phép xuất hiện | Vai trò |
|---|---|---|
| Train ban đầu | 01/01/2010–31/12/2019 | Fit mô hình và scaler |
| Validation | 01/01/2020–31/12/2021 | Chọn cấu hình, lookback, early stopping và số vòng/epoch |
| Train cuối | 01/01/2010–31/12/2021 | Refit với cấu hình đã chốt |
| Test | 01/01/2022–31/12/2023 | Chỉ đánh giá sau khi khóa lựa chọn |

Phân định bằng **ngày của toàn bộ vector nhãn**, không chỉ ngày gốc dự báo. Với mô hình 7 bước dùng chung tập mẫu, mọi nhãn của mẫu Train phải ≤ ngày cuối Train; mọi nhãn của mẫu Validation/Test phải nằm hoàn toàn trong khoảng tương ứng.

- Train ban đầu: gốc cuối 24/12/2019, nhãn cuối 31/12/2019.
- Validation: gốc từ 31/12/2019 đến 24/12/2021, tổng 725 vector nếu lịch sử đủ và không thiếu dữ liệu.
- Refit: gốc cuối 24/12/2021, nhãn cuối 31/12/2021.
- Test: gốc từ 31/12/2021 đến 24/12/2023, tổng **724 vector**, mỗi vector 7 nhãn; 5.068 cặp `(origin,horizon)` cho mỗi mô hình.
- Gốc 31/12/2021 chỉ dùng dữ liệu đến hết 2021 và phát hành nhãn 01–07/01/2022, nên vẫn thuộc giao thức Test 2022–2023. Nếu muốn gốc đầu tiên đúng 01/01/2022, tổng còn 723 vector và 5.061 cặp; phải ghi rõ và dùng nhất quán cho mọi mô hình. Kế hoạch chọn 724 gốc.
- Các cửa sổ lịch sử được phép đi qua ranh giới tập. Ví dụ dự báo 01/01/2022 dùng dữ liệu cuối 2021 là hợp lệ.
- Không bắt buộc thêm gap tùy ý nếu đã chặn nhãn chính xác. Nếu sử dụng `TimeSeriesSplit`, đặt gap dựa trên độ chồng nhãn và kiểm tra bằng ngày; không chỉ mặc định `gap=7` rồi cho rằng đã an toàn.

Nếu thêm kiểm tra độ ổn định, dùng expanding folds trong 2010–2021: Train đến 2015 → Validation 2016–2017; Train đến 2017 → Validation 2018–2019; Train đến 2019 → Validation 2020–2021. Đây là phân tích bổ sung, không kéo Test vào chọn tham số.

### 7.3. Quy tắc chống rò rỉ

1. Cấm chia ngẫu nhiên, random K-fold hoặc shuffle dữ liệu trước khi tạo cửa sổ.
2. Định nghĩa lag: `lag_0 = q_t`, `lag_k = q_(t-k)`. Tại gốc `t` dùng `q_t` là hợp lệ vì đã quan trắc.
3. Rolling window tại gốc `t` chỉ dùng `q_(t-w+1)…q_t`. Nếu index của bảng là ngày mục tiêu thay vì ngày gốc, phải `shift` phù hợp trước rolling; viết test để kiểm tra cả hai cách biểu diễn.
4. Scaler/imputer/feature selection fit trên Train của đúng lần chạy; khi refit có thể fit lại trên toàn bộ 2010–2021.
5. Không đưa thành phần STL được fit trên cả chuỗi vào đặc trưng dự báo. STL toàn chuỗi chỉ phục vụ mô tả Q1.
6. Không centered rolling hoặc backward fill sử dụng tương lai trong nhánh forecasting.
7. Không dùng ngưỡng Q95 toàn chuỗi cho trọng số loss, chọn mô hình hoặc đánh giá dự báo cực trị. Khi cần đánh giá nhóm high-flow, dùng Q95 của tập Train tương ứng.
8. Cùng một vector 7 ngày phải được sinh hoàn chỉnh trước khi sử dụng quan trắc ngày tiếp theo ở rolling-origin.
9. Không refit trên Test theo ngày trong giao thức chính. Nếu làm online retraining, tách thành thực nghiệm mở rộng và ghi rõ.
10. Batching GRU mặc định `shuffle=False` để bám yêu cầu không xáo trộn; luôn tách theo thời gian trước mọi thao tác batch.

### 7.4. Chuẩn đánh giá

Với mỗi horizon `h`, dùng cùng danh sách gốc `i=1…N`, giá trị thật `y_ih` và dự báo `p_ih`:

```math
RMSE_h = sqrt((1/N) * sum_i (p_ih - y_ih)^2)
MAE_h = (1/N) * sum_i |p_ih - y_ih|
NSE_h = 1 - sum_i (p_ih - y_ih)^2 / sum_i (y_ih - mean_i(y_ih))^2
```

- RMSE và MAE: đơn vị m³/s, càng thấp càng tốt. NSE không có đơn vị, càng gần 1 càng tốt.
- NSE = 0 tương đương dùng trung bình của các quan trắc đang được đánh giá; NSE < 0 là kém hơn mốc này. Trung bình Test trong mẫu số NSE chỉ dùng cho đánh giá, không dùng để phát hành dự báo.
- Nếu mẫu số bằng 0, trả `null` và ghi chú không xác định; không tự đổi thành 0 hoặc 1.
- Bảng chính: `mean_RMSE_7 = mean_h(RMSE_h)`, `mean_MAE_7`, `mean_NSE_7`, đồng thời có RMSE và NSE tại D+7. Ghi rõ đây là trung bình theo horizon.
- Xuất thêm pooled metrics trên toàn bộ 5.068 cặp để tra cứu; tên trường phải có `pooled_`. Pooled RMSE không mặc nhiên bằng mean RMSE. Không trộn hai cách tổng hợp giữa web và báo cáo.
- Chọn cấu hình theo mean RMSE trên Validation; nếu sai khác dưới 1% ưu tiên mô hình đơn giản hơn. Công bố tiêu chí trước Test.
- Với cùng horizon, cùng nhãn và cùng mẫu, NSE tương đương một phép biến đổi của MSE; dùng điều này để kiểm tra thứ hạng tính toán.
- Không gọi 5.068 cặp dự báo là 5.068 ngày quan trắc độc lập; các cửa sổ chồng nhau. Nếu cần khoảng tin cậy chênh lệch metric, dùng bootstrap theo khối thời gian, không bootstrap từng dòng độc lập.

## 8. Phase 0 — Chốt yêu cầu và khởi tạo dự án

**Phụ thuộc:** bốn tệp tài liệu đầu vào. **Ước lượng:** 0,5 ngày công.

- [ ] **P0.1 — Đọc và đối chiếu tài liệu.** Trích text DOCX/PDF, xem trực quan bìa và một số trang nội dung có bảng/hình. Ghi `requirements.md`, xác nhận giới hạn 5 trang và thông tin mục 1.2.
- [ ] **P0.2 — Tạo thư mục và metadata.** Tạo cây mục 6, `metadata.tex`, metadata JSON dùng cho website; chưa tạo chỉ số dự báo giả.
- [ ] **P0.3 — Lưu đầu vào bất biến.** Copy CSV vào `code/data/raw/`, tính SHA256; không sửa trực tiếp CSV gốc ở root. Ghi data dictionary.
- [ ] **P0.4 — Khởi tạo môi trường.** Editable Python package theo `pyproject.toml`; môi trường riêng; Node dependencies khóa bằng npm lockfile. Ghi phiên bản runtime và lệnh cài.
- [ ] **P0.5 — Khóa phương pháp.** Ghi mục 7 vào `methodology.md`, tạo config chia tập, horizon, seed=42, timezone xử lý ngày và output paths.
- [ ] **P0.6 — Tạo bộ khung chạy tối thiểu.** Python CLI đọc CSV và audit; web hiển thị khung điều hướng với dữ liệu thật; LaTeX biên dịch bìa và phần khung, placeholder có nhãn “chưa có kết quả”.

**Gate G0:** cả Python, website và LaTeX có thể chạy/build; thông tin tác giả và ma trận yêu cầu đúng. Không bắt đầu chọn mô hình khi giao thức còn mơ hồ.

## 9. Phase 1 — Kiểm tra dữ liệu và hợp đồng đầu vào

**Phụ thuộc:** G0. **Ước lượng:** 0,5 ngày công.

- [ ] **P1.1 — Parse nghiêm ngặt.** Đọc `date` theo `%Y-%m-%d`, xác nhận unique index, đúng kiểu số và thứ tự.
- [ ] **P1.2 — Kiểm tra lịch.** Đối chiếu với `date_range` đầy đủ, giữ các ngày nhuận 2012/2016/2020. Không loại 29/02 để làm cho năm bằng nhau.
- [ ] **P1.3 — Kiểm tra giá trị.** Missing, nonfinite, âm, zero-run, duplicate, bước nhảy bất thường. Chỉ gắn cờ nghi vấn; không xóa đỉnh cao vì là outlier.
- [ ] **P1.4 — Tạo báo cáo chất lượng.** Xuất `data_quality.json`, bảng thống kê cơ bản, checksum và phạm vi quan trắc.
- [ ] **P1.5 — Chính sách missing nếu phát sinh.** Dataset hiện không thiếu nên không nội suy. Nếu bản dữ liệu khác phát sinh thiếu: tách dữ liệu mô tả với dữ liệu mô hình; input có thể causal imputation fit Train, target thiếu không được bù giả để chấm điểm. Ghi số mẫu loại.
- [ ] **P1.6 — Tạo processed dataset.** Thêm cột calendar cần thiết, giữ precision gốc trong file máy đọc; chỉ làm tròn khi hiển thị.
- [ ] **P1.7 — Viết test dữ liệu.** Assert 5.113 ngày, đúng min/max date, không trùng/thiếu; đối chiếu mốc thống kê mục 3 với tolerance hợp lý.

**Output:** processed CSV/Parquet, data dictionary, quality JSON, bảng chất lượng. **Gate G1:** số liệu tái lập được và không có biến đổi dữ liệu âm thầm.

## 10. Phase 2 — Phân tích xu hướng và mùa vụ để trả lời Q1

**Phụ thuộc:** G1. **Ước lượng:** 0,75–1 ngày công.

- [ ] **P2.1 — Thống kê theo ngày, tháng, năm.** Mean, median, sample std, min, max, Q05/Q25/Q75/Q95; trung bình năm, trung bình tháng từng năm và chu trình 12 tháng.
- [ ] **P2.2 — Biểu diễn xu hướng.** Vẽ chuỗi ngày, đường trung bình trượt 30/365 ngày và trung bình năm. Nếu centered smoothing được dùng để mô tả hồi cứu, ghi rõ không dùng cho forecasting.
- [ ] **P2.3 — Phân rã STL.** Chọn robust STL ở tần suất ngày với period=365 như xấp xỉ chu kỳ năm; giữ ngày nhuận, giải thích sai khác lịch. Có thể đối chiếu STL chuỗi tháng period=12 để kiểm tra độ ổn định kết luận.
- [ ] **P2.4 — Kiểm tra mùa vụ.** Boxplot theo tháng; đường trung bình/median tháng với dải IQR; ACF phần đã tách xu hướng tại các lag phù hợp, đặc biệt quanh 365 ngày. ACF chuỗi gốc chỉ là tham khảo vì trend có thể làm ACF cao giả tạo.
- [ ] **P2.5 — Kiểm tra theo từng năm.** Heatmap năm × tháng và biên độ chu kỳ từng năm; đối chiếu toàn chuỗi với chuỗi đã detrend. Không chỉ nhìn trung bình 14 năm.
- [ ] **P2.6 — Diễn giải có căn cứ.** Trả lời xu hướng tăng/giảm ở giai đoạn nào, tháng cao/thấp, biên độ mùa vụ so với biến thiên nhiều năm, chu kỳ có lặp ổn định không.
- [ ] **P2.7 — Kết luận thận trọng.** Nếu xu hướng phi tuyến, mô tả theo giai đoạn thay vì chỉ fit một đường thẳng và kết luận tăng dài hạn. Nếu mùa vụ yếu, nói rõ bằng số liệu; không cố viết có lũ mùa xuân vì kiến thức chung về Colorado.
- [ ] **P2.8 — Xuất asset.** `trend_seasonality.pdf/png`, monthly/yearly tables và phần findings Q1, ghi từng nhận xét gắn với mã bảng/hình.

Có thể tính seasonal strength từ các thành phần STL, nhưng phải định nghĩa công thức và xem đây là chỉ số bổ trợ. Không bắt buộc thêm kiểm định xu hướng gây phức tạp; nếu dùng p-value phải xử lý tự tương quan và giới hạn chuỗi 14 năm.

**Gate G2:** Q1 có hình, bảng và diễn giải thực chất; dữ liệu dùng cho quyết định dự báo vẫn giới hạn ở Train/Validation.

## 11. Phase 3 — Phân tích cực trị và Z-score để trả lời Q2

**Phụ thuộc:** G1; có thể song song Phase 2. **Ước lượng:** 0,5–0,75 ngày công.

### 11.1. Phương pháp chính bắt buộc

Chọn **Z-score tĩnh với ngưỡng hiệu chỉnh theo Q95 thực nghiệm** để đồng thời đáp ứng yêu cầu Z-score và Top 5%:

```math
z_t = (q_t - mu) / s
u = quantile_0.95(q_2010:2023)
z_95 = (u - mu) / s
extreme_t = (q_t > u) = (z_t > z_95)
```

`mu` và `s` được tính trên toàn chuỗi cho phân tích mô tả hồi cứu Q2. Ghi rõ phạm vi này. Không gọi `z > 3` là Top 5%; không dùng 1,645 như thể phân bố lưu lượng chắc chắn chuẩn. Với file hiện tại, ngưỡng Z95 khoảng 1,224 chứ không phải 1,645.

- [ ] **P3.1 — Tính Q95 và Z-score.** Nội suy tuyến tính, sample std, điều kiện `>`; kiểm tra số điểm và tỷ lệ vượt ngưỡng.
- [ ] **P3.2 — Vẽ toàn chuỗi.** Trục thời gian đủ 2010–2023, đường Q95, điểm đỏ vượt Q95, vùng đợt high-flow, legend và đơn vị rõ ràng. Dữ liệu hiển thị thu gọn không được làm mất các cực đại.
- [ ] **P3.3 — Gom đợt.** Một đợt là dãy ngày liên tiếp `q>Q95`; khoảng cách một ngày không vượt ngưỡng kết thúc đợt. Xuất start/end/duration/peak_date/peak_flow/n_exceedance_days.
- [ ] **P3.4 — Phân biệt đợt và đỉnh cục bộ.** Nếu một đợt dài có nhiều cực đại, có thể nhận diện đỉnh cục bộ bổ sung; đây không phải cùng khái niệm với số đợt. Không tự nhận các đợt độc lập về mặt thủy văn.
- [ ] **P3.5 — Bảng sự kiện.** Top 5 đợt theo lưu lượng đỉnh trên báo cáo; danh sách đầy đủ trên website, tải CSV.
- [ ] **P3.6 — Thống kê theo năm/tháng.** Số ngày high-flow và số đợt; ghi rõ mẫu số tỷ lệ.
- [ ] **P3.7 — Nhận xét.** Sự kiện tập trung giai đoạn nào, đỉnh cao có đi kèm đợt dài không, tác động của nền dòng chảy nhiều năm lên ngưỡng tĩnh.

### 11.2. Moving Z-score bổ sung

- [ ] **P3.8 — Nếu triển khai, dùng cửa sổ 30 ngày trước t**, không bao gồm ngày t: `mean/std` từ `q_(t-30)…q_(t-1)`; 30 ngày đầu không có score, std=0 trả missing.
- [ ] **P3.9 — Hiển thị hai lớp riêng:** “Top 5% toàn chuỗi” và “Bất thường so với 30 ngày trước”. Ngưỡng moving Z mặc định 2 là lựa chọn khảo sát, có chú giải, không diễn giải như Top 5% toàn chuỗi.
- [ ] **P3.10 — Không dùng moving Z để thay thế lớp highlight Q95 bắt buộc.** Website cho bật/tắt lớp phụ; báo cáo ưu tiên phương pháp tĩnh để tiết kiệm trang.

“Sự kiện lưu lượng cao” là tên chính xác khi chưa có ngưỡng báo động và thông tin thiệt hại. Có thể dùng “đỉnh lũ theo ngưỡng thống kê của bài tập”, nhưng phải phân biệt với lũ đã được cơ quan quản lý xác nhận.

**Gate G3:** hình đủ 14 năm; Q95 đúng; số ngày và số đợt không nhầm; bảng/hình/web nhất quán.

## 12. Phase 4 — Tạo tập dự báo và bộ đặc trưng

**Phụ thuộc:** G1 và phương pháp mục 7 đã khóa. **Ước lượng:** 0,75 ngày công.

- [ ] **P4.1 — Tạo split manifest.** Ghi ngày Train/Validation/Test, ngày gốc hợp lệ và ngày mục tiêu; kiểm tra đủ các cửa sổ 7 ngày.
- [ ] **P4.2 — Đặc trưng lưu lượng.** `q_t`, lag 1/2/3/7/14/21/28/30 ngày; rolling mean/std/min/max trên 7/14/30 ngày; chênh `q_t-q_(t-1)` và `q_t-q_(t-7)`.
- [ ] **P4.3 — Đặc trưng lịch.** Sin/cos day-of-year và month. Định nghĩa rõ cách xử lý năm nhuận; ví dụ day-of-year chia số ngày thực tế của năm. LightGBM horizon h có thể dùng calendar của ngày mục tiêu t+h vì biết trước.
- [ ] **P4.4 — Nhóm lag dài.** Lag 60/90/365 chỉ thêm như cấu hình thử trên Validation. Nếu thêm lag365, mọi mô hình phải so sánh trên giao tập gốc hợp lệ chung, không để thay đổi mẫu đánh giá âm thầm.
- [ ] **P4.5 — Lookback GRU.** Thử L trong {30,60,90}. Input gồm lưu lượng chuẩn hóa và lịch tại các ngày đã biết; tương lai chỉ có lịch nếu xây nhánh riêng được tài liệu hóa.
- [ ] **P4.6 — Chuẩn hóa.** StandardScaler fit Train cho GRU; target dùng cùng thang lưu lượng và inverse transform trước chấm điểm. LightGBM không bắt buộc scale.
- [ ] **P4.7 — Các test quan trọng.** Với một gốc kiểm thử, in input dates, max input date, 7 target dates và assertions. Sửa giá trị q sau t phải không làm đổi features tại t. Sửa target Validation/Test không được làm đổi fitted scaler Train.
- [ ] **P4.8 — Không điền target giả.** Loại những hàng thiếu lịch sử hoặc không đủ 7 nhãn; ghi số lượng và lý do.

**Gate G4:** mọi input có timestamp ≤ origin; mọi target nằm trong partition; Test chính có 724 vector đồng nhất cho tất cả mô hình.

## 13. Phase 5 — Baseline và LightGBM

**Phụ thuộc:** G4. **Ước lượng:** 0,75–1 ngày công.

- [ ] **P5.1 — Naive persistence.** Tại mỗi gốc t: dự báo cả 7 ngày bằng q_t. Đây là baseline bắt buộc và có thể rất mạnh ở chuỗi trơn/tự tương quan cao.
- [ ] **P5.2 — Seasonal Naive.** Dùng `q_(t+h-365)` cho h=1…7; ghi rõ độ trễ cố định 365 ngày là xấp xỉ lịch năm, chưa xử lý đối sánh tháng-ngày. Không giả định baseline này tốt nếu mùa vụ yếu.
- [ ] **P5.3 — LightGBM direct.** Tạo 7 `LGBMRegressor`, dùng chung tập gốc có đủ 7 nhãn. Lưu riêng model của từng horizon.
- [ ] **P5.4 — Cấu hình khởi đầu.** Objective regression, learning_rate=0.03, n_estimators tối đa 1.000, num_leaves=15, max_depth=5, min_child_samples=30, reg_lambda=1, n_jobs tối đa 4; seed=42.
- [ ] **P5.5 — Tuning có ngân sách.** Tối đa 16 cấu hình được lấy ngẫu nhiên có seed từ các tập: learning_rate {0.03,0.05}; num_leaves {7,15,31}; max_depth {3,5,-1}; min_child_samples {20,40,80}; reg_lambda {0,1,5}; nhóm lag dài bật/tắt. Loại tổ hợp bất hợp lý về số lá/độ sâu.
- [ ] **P5.6 — Early stopping.** Validation 2020–2021, patience=50 rounds cho từng horizon. Lưu best_iteration từng mô hình. Không truyền chung một vector y của horizon khác vào eval_set.
- [ ] **P5.7 — Chọn cấu hình.** Xếp theo mean RMSE Validation; lưu toàn bộ trials, không chỉ model tốt nhất. Kiểm tra D+7 và sai số theo năm để hiểu độ ổn định, không thay tiêu chí sau khi thấy Test.
- [ ] **P5.8 — Feature importance.** Xuất gain importance theo horizon hoặc trung bình; không diễn giải đó là quan hệ nhân quả. Nếu chỉ q_t/lag gần chi phối, giải thích vai trò persistence.
- [ ] **P5.9 — Smoke test pipeline.** Chạy baseline + một cấu hình LightGBM xuyên suốt, xác nhận schema dự báo và export trước khi mở rộng tuning.

**Gate G5:** baseline và LightGBM có dự báo Validation hợp lệ, metric thật và model lưu được; chưa chấm Test để chọn tham số.

## 14. Phase 6 — GRU và huấn luyện local CPU

**Phụ thuộc:** G4; có thể song song phần tuning Phase 5. **Ước lượng:** 0,75–1,5 ngày công; thời gian train đo thực tế.

### 14.1. Thực nghiệm GRU

- [ ] **P6.1 — Model nhỏ.** GRU 1 layer, hidden_size=32, đầu cuối Linear(32,7); unidirectional, batch_first=True. Không dùng bidirectional như một thành phần cần thiết.
- [ ] **P6.2 — Huấn luyện.** MSE loss, Adam lr=1e-3, batch_size=64, tối đa 150 epochs, early stopping 15 epochs, gradient clipping=1.0. Checkpoint theo mean RMSE Validation ở đơn vị gốc.
- [ ] **P6.3 — Ngân sách thử.** L ∈ {30,60,90}, hidden_size ∈ {32,64}; tối đa 6 cấu hình, cùng seed42. Có thể thử 3 seed cho cấu hình đã chọn nếu tài nguyên cho phép; không chọn seed đẹp nhất rồi giấu các seed khác.
- [ ] **P6.4 — Kiểm tra thang đo.** Metrics sau inverse scaling, đúng shape `[N,7]`, không teacher forcing sử dụng nhãn tương lai khi đánh giá.
- [ ] **P6.5 — Lưu tái lập.** State dict, cấu hình kiến trúc, scaler, best epoch, lịch sử loss/metric, seed, runtime và dependency versions.

### 14.2. Huấn luyện local CPU

Dataset chỉ có 5.113 ngày và mô hình rất nhỏ, nên LightGBM và GRU chạy CPU tại máy hiện tại là đủ. Không cần server, GPU hay thông tin đăng nhập từ xa. Nếu về sau thật sự cần train từ xa, dùng SSH key và biến môi trường; không lưu host, user, mật khẩu hay token trong plan, source, notebook, log hoặc ZIP.

- [ ] **P6.6 — Preflight local.** Xác nhận `python3 --version`, `pip list`, `free -h`, `df -h`, `nproc` và dung lượng trống trước khi cài PyTorch; không giả định tài nguyên còn đủ nếu chưa kiểm tra.
- [ ] **P6.7 — Môi trường riêng.** Tạo `.venv` trong `code/`; không cài đè package hệ thống. Khóa phiên bản thực tế vào `requirements.lock.txt`.
- [ ] **P6.8 — Cài PyTorch CPU-only.** Chỉ cài bản CPU nếu thực hiện GRU; kiểm tra `torch.cuda.is_available()` là `False` và ghi rõ môi trường CPU trong log.
- [ ] **P6.9 — Chọn CPU/GPU.** LightGBM mặc định CPU, `n_jobs=4`. GRU dùng CPU với batch nhỏ; nếu RAM không đủ, giảm batch hoặc hidden_size và ghi lại cấu hình đã dùng.
- [ ] **P6.10 — Chạy bền local.** Dùng tmux hoặc `nohup` nếu train lâu; lưu stdout/stderr, thời gian bắt đầu/kết thúc trong `results/logs/`.
- [ ] **P6.11 — Theo dõi.** Chỉ kiểm tra log và PID do job của dự án tạo ra; không can thiệp process khác.
- [ ] **P6.12 — Lưu kết quả.** Giữ checkpoint, scaler, config, log, manifest và predictions trong `results/`; xác nhận model load lại và chạy inference mẫu trước khi chấm Test.

**Gate G6:** GRU có lịch sử train và Validation thật, hoặc có ghi nhận rõ giới hạn thực thi; cơ chế tái lập và tải model hoạt động.

## 15. Phase 7 — Khóa mô hình và đánh giá Test

**Phụ thuộc:** G5/G6, toàn bộ chọn tham số hoàn thành. **Ước lượng:** 0,75 ngày công.

- [ ] **P7.1 — Ghi biên bản khóa.** `model_selection.json` ghi cấu hình từng model, features, lookback, số rounds/epoch, tiêu chí chọn, seed và hash config; thực hiện trước evaluate Test.
- [ ] **P7.2 — Refit trên 2010–2021.** Scaler fit lại tập này. LightGBM dùng số rounds đã chọn từ Validation cho từng horizon; GRU dùng số epoch đã chọn, không early-stop bằng Test.
- [ ] **P7.3 — Chạy rolling-origin.** Gốc 31/12/2021–24/12/2023. Sau mỗi ngày chỉ cập nhật lịch sử quan trắc, không cập nhật trọng số trong giao thức chính.
- [ ] **P7.4 — Xuất bảng dài.** Mỗi dòng một `(run_id,model,origin_date,target_date,horizon,y_true,y_pred)`; không trùng khóa, không missing, target=origin+h ngày.
- [ ] **P7.5 — Tính chỉ số.** Mỗi horizon, macro theo7 horizon, pooled, theo năm của ngày mục tiêu. Ghi n và đơn vị; bảo đảm mô hình dùng chung tập mẫu.
- [ ] **P7.6 — Phân tích sai số.** Đường RMSE/MAE/NSE theo horizon; hydrograph D+1 và D+7; scatter observed–predicted và residual plot. Khi vẽ liên tục, cố định horizon để mỗi target date chỉ có một dự báo.
- [ ] **P7.7 — Phân tích high-flow nếu có đủ mẫu.** Ngưỡng lấy từ 2010–2021; báo n và RMSE/MAE trong nhóm target > Q95_train. Nếu ít/không có điểm, ghi không đủ mẫu; không hạ ngưỡng sau khi thấy Test.
- [ ] **P7.8 — Chọn mô hình hiển thị mặc định.** Dùng lựa chọn từ Validation. Test dùng để mô tả hiệu suất cuối, không quay lại tuning để làm đẹp kết quả.
- [ ] **P7.9 — Dự báo minh họa cuối chuỗi.** Từ gốc 31/12/2023 dự báo 01–07/01/2024; tách file riêng, không có y_true và không tính metrics. Đây là minh họa ngoài khoảng quan trắc, không phải dự báo thời gian thực năm 2026.
- [ ] **P7.10 — Kiểm tra kết luận.** Nếu Naive tốt nhất, báo đúng và giải thích có bằng chứng. Nếu LightGBM/GRU chỉ hơn ở vài horizon, không kết luận thắng toàn diện. Không sửa dữ liệu, loại ngày khó hoặc thay split để đảo kết quả.

**Output:** predictions, metrics, diagnostics, frozen models, `findings.md`. **Gate G7:** mỗi số được báo cáo truy được về file kết quả và giao thức chấm điểm.

## 16. Phase 8 — Thiết kế website

**Phụ thuộc:** schema kết quả đã chốt; có thể dựng giao diện sau G1, kết nối metrics sau G7. **Ước lượng:** 0,75 ngày công.

### 16.1. Nguyên tắc giao diện

- Nền sáng `#F8FAFC`, panel trắng, chữ `#0F172A`; xanh chính `#1D4ED8`, teal `#0F766E`, cực trị đỏ `#DC2626`, baseline xám. Không dựa vào màu đơn thuần: dùng legend, nét đứt và marker.
- Header gọn: tên dự án, thời đoạn, liên kết tải PDF; desktop sidebar hoặc thanh điều hướng rõ; mobile menu có nhãn.
- Font giao diện hỗ trợ tiếng Việt, tối thiểu 16 px cho nội dung; không chữ quá nhỏ ở bảng/tooltip. Chart có tiêu đề và mô tả một câu nêu câu hỏi đang trả lời.
- Ưu tiên chart chiếm chiều rộng hữu ích; tối đa 4 KPI đầu trang. Không xếp hàng chục card hoặc dùng hiệu ứng làm khó đọc dữ liệu.
- Bộ lọc ghi rõ phạm vi: thay khoảng ngày có thể thay KPI/biểu đồ đang xem nhưng không tính lại ngưỡng Q95 cố định nếu không có chế độ được gắn nhãn rõ.
- Ngày hiển thị `dd/mm/yyyy`, dữ liệu máy đọc ISO `yyyy-mm-dd`. Tránh parse JavaScript làm lệch ngày do timezone; đây là ngày quan trắc, không phải timestamp cần quy đổi múi giờ.
- Biểu đồ có tooltip, zoom/reset, legend toggle và tải PNG; bảng có sort/filter/download CSV. Các tính năng phải hoạt động thật.

### 16.2. Nội dung từng trang

| Trang | Nội dung và thao tác | Câu hỏi người dùng được giải đáp |
|---|---|---|
| Tổng quan | Thời đoạn, 5.113 ngày, lưu lượng TB/max, hydrograph thu gọn, 3 lối vào Q1/Q2/Q3 | Bộ dữ liệu gồm gì, điểm chính ở đâu? |
| Khám phá dữ liệu | Chọn ngày/khoảng năm; chuỗi ngày, bảng dữ liệu, nút tải | Ngày này lưu lượng bao nhiêu, so với giai đoạn khác thế nào? |
| Xu hướng và mùa vụ | Trend, STL, boxplot tháng, heatmap năm×tháng; ghi chú detrend | Có xu hướng và chu kỳ năm rõ không? |
| Lưu lượng cao | Toàn chuỗi Q95, lớp Z-score, danh sách đợt, nhấp đợt để zoom | Ngày/đợt nào vượt Top5%, kéo dài bao lâu? |
| Dự báo 7 ngày | Chọn origin, model, 7 giá trị; lịch sử ≤ origin và forecast nét đứt; ground truth tùy bật trong backtest | Tại ngày được chọn, 7 ngày sau được dự báo thế nào? |
| So sánh mô hình | RMSE/MAE/NSE, horizon, năm; bảng và giải thích chiều tốt/xấu | Mô hình nào hiệu quả theo tiêu chí đã khóa? |
| Phương pháp | Split timeline, lag, ngưỡng, metric, nguồn, giới hạn dữ liệu | Kết quả được tính thế nào? |
| Tải xuống | CSV gốc/processed/predictions/metrics, báo cáo PDF và source khi có | Có thể kiểm tra và tái lập ở đâu? |

### 16.3. Quy tắc trang dự báo

1. Phân biệt “Kiểm thử lịch sử 2022–2023” với “Minh họa 01–07/01/2024”. Không đặt badge “Live”.
2. Tại origin t, đường lịch sử mặc định chỉ đến t. Bảy dự báo được phát hành cùng lúc; phần thật ở tương lai t chỉ xuất hiện khi người xem bật đối chiếu backtest.
3. Chọn origin trong khoảng hợp lệ theo manifest, tránh cho người dùng chọn ngày không có đủ 7 nhãn rồi hiển thị dở dang.
4. Cửa sổ ban đầu hiển thị khoảng 60 ngày lịch sử + 7 ngày dự báo; có thể zoom, không vẽ toàn bộ 14 năm cho một dự báo ngắn.
5. Hiển thị bảng D+1…D+7 kèm ngày, dự báo, quan trắc nếu có, sai số. Không trộn RMSE tính trên 7 ngày của một origin với RMSE toàn tập; ghi phạm vi rõ.
6. Không vẽ dải tin cậy giả. Chỉ thêm interval nếu đã hiệu chỉnh bằng dữ liệu trước Test và có kiểm tra coverage; mặc định không có interval.

**Gate G8:** có wireframe hoặc ảnh prototype cho Tổng quan, Cực trị, Dự báo; user flow rõ, không cần backend hay tọa độ trạm giả.

## 17. Phase 9 — Xây dựng website và kiểm chứng dữ liệu hiển thị

**Phụ thuộc:** G8 và kết quả thật G2/G3/G7. **Ước lượng:** 1–2 ngày công.

- [ ] **P9.1 — App shell và điều hướng.** Dùng hash routing hoặc phương án tương thích hosting tĩnh; URL có thể giữ tab, model, origin, khoảng ngày.
- [ ] **P9.2 — Định nghĩa TypeScript schema.** `Manifest`, `DailyObservation`, `ExtremeEvent`, `ForecastRow`, `MetricRow`; xác thực dữ liệu nạp vào, xử lý lỗi tải file.
- [ ] **P9.3 — Export manifest.** Gồm dataset_hash, run_id, created_at, split, metric_aggregation, model list, threshold scope và schema_version.
- [ ] **P9.4 — Tách dữ liệu hợp lý.** Daily series một file nhỏ; predictions tách theo model/năm nếu cần. Không nhúng model weights vào bundle giao diện.
- [ ] **P9.5 — Tích hợp chart.** Full-series line với Q95 và scatter cực trị; seasonality boxplot/heatmap; forecast có observed/predicted khác nét; metric-horizon dùng trục và đơn vị đúng.
- [ ] **P9.6 — Bảng và tải xuống.** Download dữ liệu đúng bộ lọc; tên file có phạm vi; lỗi/empty state có thông báo. Dùng asset đường dẫn tương thích Vite base dưới subpath.
- [ ] **P9.7 — Nội dung diễn giải.** Mỗi trang có kết luận ngắn lấy từ findings đã rà soát; không dùng nội dung chung chung như “AI chính xác cao”.
- [ ] **P9.8 — Responsive và accessibility.** Test 375 px, 768 px, 1440 px; keyboard navigation, focus visible, contrast; bảng rộng cuộn trong panel, không làm toàn trang tràn ngang.
- [ ] **P9.9 — Kiểm tra số liệu.** So sánh số trên 4 KPI, Q95, số ngày extreme và metric từng model với CSV/JSON gốc bằng test hoặc kiểm tra schema tự động.
- [ ] **P9.10 — Kiểm thử thao tác.** Chọn event→zoom đúng ngày; đổi origin→đủ 7 bước; đổi model→đúng forecast; bật ground truth→chỉ chế độ backtest; tải file→khớp dữ liệu.
- [ ] **P9.11 — Build/preview.** Typecheck, production build, browser console không lỗi; kiểm tra không cần gọi API bên ngoài để xem dữ liệu cốt lõi.
- [ ] **P9.12 — Triển khai khi đủ công cụ/quyền.** Ưu tiên repo mới riêng và GitHub Pages nếu tài khoản có kết nối sẵn; không ghi đè website của bài trước. Nếu chưa publish được, bàn giao `dist/`, source và hướng dẫn, ghi URL chưa có; không tự tạo liên kết tưởng tượng.

**Gate G9:** website chạy từ production build, dữ liệu thật, các nút hoạt động; có ảnh chụp các luồng chính để kiểm tra và minh họa hướng dẫn.

## 18. Phase 10 — Tạo LaTeX và viết báo cáo theo mẫu

**Phụ thuộc:** khung có thể tạo từ G0; nội dung cuối sau G7/G9. **Ước lượng:** 1–1,5 ngày công.

### 18.1. Khung Overleaf độc lập

- [ ] **P10.1 — `main.tex`.** `article`, A4, 12pt, margin khoảng 2 cm, XeLaTeX; điều chỉnh hợp lý sau render, không ép bằng cỡ chữ quá nhỏ.
- [ ] **P10.2 — `preamble.tex`.** `fontspec`, `babel` với tùy chọn `vietnamese`, `graphicx`, `booktabs`, `tabularx`, `amsmath`, `siunitx`, `caption`, `hyperref`, `biblatex` hoặc `natbib`. Không dùng package không cần thiết hoặc phụ thuộc font máy cá nhân.
- [ ] **P10.3 — `metadata.tex`.** Tập trung tên trường/khoa/tác giả/ngành/khóa/giảng viên/năm và tiêu đề. Dùng đúng GS. Đỗ Minh Đức.
- [ ] **P10.4 — Bìa.** Dựa phong cách mẫu: khung viền gọn, trường/khoa ở trên, dùng `latex/assets/logo_dhkhtn.jpg` ở kích thước nhỏ nếu ảnh đủ rõ hoặc bỏ logo, “BÁO CÁO KẾT QUẢ”, tiêu đề mới, bảng thông tin tác giả và “Hà Nội, 2026”. Bìa tính là trang 1 trong giới hạn 5 trang.
- [ ] **P10.5 — Sinh bảng/số tự động.** `export_latex.py` ghi `.tex` table và `generated/numbers.tex`; `main.tex` chỉ `\input` file trong folder latex. Không đọc đường dẫn `../code` lúc biên dịch Overleaf.
- [ ] **P10.6 — Copy asset cuối.** Figure PDF vector, PNG 300 dpi nếu cần, tên ASCII không khoảng trắng; tất cả references là đường dẫn tương đối trong gói; copy `logo_dhkhtn.jpg` nếu dùng.
- [ ] **P10.7 — Hướng dẫn Overleaf.** Upload ZIP, chọn XeLaTeX, main=`main.tex`, compile; ghi quy trình bibliography và font thay thế. Nếu dùng biblatex, cấu hình biber và kiểm tra đủ citation.

### 18.2. Phân bổ 5 trang bắt buộc

| Trang | Nội dung | Asset ưu tiên |
|---|---|---|
| 1 | Bìa theo mẫu và thông tin tác giả | Logo hợp lệ nếu có; không mục lục |
| 2 | 1. Dữ liệu/công cụ; 2. Chất lượng; 3. Xu hướng/mùa vụ, trả lời Q1 | Bảng chất lượng gọn; Hình 1 gồm trend, chu trình tháng và heatmap nhỏ hoặc STL |
| 3 | 4. Lưu lượng cao, Q2; công thức Q95/Z; nhận xét đợt; 5.1. Giao thức chia tập/dự báo | Hình 2 toàn chuỗi có highlight; Bảng 3–5 đợt tiêu biểu; split text/timeline ngắn |
| 4 | 5.2. Mô hình/đặc trưng; 5.3. RMSE/MAE/NSE; bảng kết quả Test | Bảng mô hình chính; Hình 3 RMSE theo horizon; công thức viết gọn, dễ đọc |
| 5 | 5.4. Chẩn đoán dự báo; 6. Website; 7. Kết luận/hạn chế; tài liệu tham khảo | Hình 4 hydrograph D+1/D+7; URL thật hoặc hướng dẫn chạy cục bộ; 4–6 nguồn ngắn |

Mục tiêu khoảng 1.400–1.800 từ nội dung tiếng Việt, điều chỉnh theo bản render. Không mặc định thêm screenshot website vào PDF nếu làm mất chỗ cho kết quả; screenshot đầy đủ nằm trong tài liệu website. Nếu thực sự đủ chỗ có thể thêm một hình nhỏ, nhưng vẫn giữ tối đa 5 trang và chữ đọc được.

### 18.3. Công thức viết nhận xét cho từng phần

Mỗi nhận xét theo trình tự: **quan sát định lượng → đối chiếu → diễn giải có giới hạn → ý nghĩa**.

- Dữ liệu: phạm vi, mức đầy đủ, có/không xử lý thiếu, ảnh hưởng đến độ tin cậy; không viết dài khi không có lỗi.
- Trend: nêu giá trị và giai đoạn; phân biệt thay đổi nhiều năm với tính tăng/giảm đơn điệu.
- Seasonality: tháng cao/thấp và chênh lệch, độ ổn định sau detrend; nếu yếu, nói yếu. Nguyên nhân khí tượng/vận hành hồ chỉ là giả thuyết nếu không có dữ liệu bổ sung.
- High-flow: Q95, số ngày/tỷ lệ, số đợt, đỉnh và thời điểm; làm rõ ngày vượt ngưỡng khác đợt.
- Models: nêu mô hình được chọn trên Validation, mức chênh RMSE/MAE/NSE trên Test, suy giảm theo horizon, năm nào khó; không chỉ nói “tốt nhất”.
- Hydrology: phân tích liệu model làm mượt hoặc bỏ lỡ đỉnh, sai số tăng ở đoạn đổi chế độ, persistence có cạnh tranh không. Không gọi NSE cao là bảo đảm cảnh báo lũ an toàn.
- Hạn chế: một biến, một chuỗi14 năm, thiếu metadata trạm, không có mưa/tuyết/xả hồ, Test2 năm, cửa sổ chồng nhau, dự báo trung bình ngày không thể hiện đỉnh trong ngày.
- Website: chức năng tra cứu và đường dẫn kiểm chứng, nói ngắn. Website không thay thế bằng chứng khoa học trong PDF.

Không điền sẵn các từ “vượt trội”, “độ chính xác cao” hoặc “chu kỳ lũ rõ rệt” trước khi có kết quả.

### 18.4. Kiểm tra hình thức

- [ ] **P10.8 — Biên dịch.** Dùng `latexmk -xelatex main.tex` nếu có TeX Live, hoặc upload Overleaf và chọn XeLaTeX; kiểm tra tiếng Việt, math, citation và file ảnh.
- [ ] **P10.9 — Đếm trang thật.** Dùng `pdfinfo` hoặc thư viện PDF; số trang vật lý bao gồm bìa ≤ 5, không dựa vào số trang in ở footer.
- [ ] **P10.10 — Render toàn bộ.** Render cả 5 trang PNG, mở kiểm tra bìa, font, bảng, hình, khoảng trắng, tràn lề và ký hiệu m³/s; sửa và compile lại nếu có lỗi.
- [ ] **P10.11 — Rà số liệu và câu chữ.** Chỉ số/tên mô hình/thời đoạn ở phần mở đầu, bảng, caption, kết luận và website thống nhất. Thay mọi placeholder; bỏ link chưa tồn tại.
- [ ] **P10.12 — Kiểm tra ZIP sạch.** Giải nén vào thư mục tạm mới rồi compile, bảo đảm không lệ thuộc file ngoài gói. Có điều kiện thì kiểm tra trực tiếp Overleaf.

**Gate G10:** LaTeX độc lập; PDF ≤ 5 trang; mọi số có nguồn trong results; trình bày gần mẫu mà vẫn tuân thủ đề bài.

## 19. Phase 11 — Nghiệm thu tổng thể và đóng gói

**Phụ thuộc:** G9/G10. **Ước lượng:** 0,5–0,75 ngày công.

- [ ] **P11.1 — Chạy lại trên môi trường sạch.** Cài dependencies theo lockfiles trên CPU local, chạy pipeline tối thiểu hoặc load checkpoint và tái tạo metrics; website build được; LaTeX compile được trên Overleaf hoặc TeX Live nếu có.
- [ ] **P11.2 — Kiểm chứng trùng khớp.** So sánh PDF table source, website JSON và CSV metrics; cùng run_id, dataset_hash, threshold scope, precision và aggregation.
- [ ] **P11.3 — Soát bàn giao.** Không thiếu CSV đầu vào, config cuối, model metadata, lời giải Q1/Q2/Q3, source website, source LaTeX và `logo_dhkhtn.jpg` nếu dùng.
- [ ] **P11.4 — Kiểm tra secret.** Không còn mật khẩu, key, token, `.env` thật hoặc lịch sử shell nhạy cảm trong source/ZIP. Không đưa thông tin đăng nhập hoặc host train lên website.
- [ ] **P11.5 — ZIP LaTeX.** Đặt `main.tex` ngay tại root của nội dung ZIP; không kèm `.aux/.log/.synctex` hoặc dữ liệu huấn luyện không cần thiết.
- [ ] **P11.6 — ZIP source.** Include code/config/tests/lockfiles/README/dữ liệu và kết quả phục vụ demo; loại `.venv`, `node_modules`, cache, build rác, `plan.md.bak`. Include `dist/` hoặc hướng dẫn build rõ. Với model nhỏ có thể kèm checkpoint; nếu không, chỉ rõ nơi lưu và lệnh tạo lại.
- [ ] **P11.7 — Gói nộp.** Bắt buộc: PDF đúng tên. Nếu quy trình yêu cầu: kèm `latex_overleaf.zip`, `source_code.zip`, README ngắn có lệnh chạy và link website thật nếu đã publish. Lưu checksum của các deliverable.
- [ ] **P11.8 — Báo cáo trạng thái.** Chỉ rõ mục hoàn tất, test đã chạy, URL thực, giới hạn còn lại. Không nói “hoàn thành” nếu chỉ có skeleton hoặc ảnh giao diện giả.

**Gate G11:** người nhận có thể xem PDF và tái lập phân tích; nếu có hồ sơ bổ sung thì website chạy được và LaTeX biên dịch được mà không hỏi lại cấu trúc dự án.

## 20. Hợp đồng dữ liệu giữa phân tích, website và LaTeX

### 20.1. Các tệp kết quả chuẩn

| File | Nội dung tối thiểu |
|---|---|
| `run_manifest.json` | run_id, UTC timestamp, dataset_hash, git_commit nếu có, configs, dependency versions, seed, runtime |
| `data_quality.json` | n_records, date_min/max, missing_dates, duplicate_dates, nulls, invalid_values |
| `split_manifest.json` | partition boundaries, forecast definition, valid origins, n_origins, horizon, fitted preprocessing scope |
| `model_selection.json` | Validation scores, selected params, rounds/epochs, features/lookback, freeze timestamp |
| `predictions_long.csv` | run_id, model, origin_date, target_date, horizon, y_true, y_pred, split |
| `metrics_by_horizon.csv` | run_id, model, split, horizon, n, RMSE, MAE, NSE |
| `metrics_overall.csv` | model, split, mean_RMSE_7, mean_MAE_7, mean_NSE_7, pooled_RMSE/MAE/NSE, n_origins |
| `metrics_by_year.csv` | model, target_year, horizon, n, RMSE, MAE, NSE |
| `extreme_events.csv` | event_id, start_date, end_date, duration_days, peak_date, peak_flow, threshold_value, threshold_scope |
| `web/public/data/manifest.json` | schema_version, run_id, dataset_hash, file list, models, date scopes, threshold/metric definitions |
| `latex/generated/numbers.tex` | Các macro định dạng số được sinh từ đúng results của run cuối |

JSON không chứa NaN/Infinity; giá trị không xác định dùng `null`. CSV dùng UTF-8, dấu chấm thập phân; website và LaTeX tự định dạng số Việt Nam khi hiển thị. Lưu đủ precision trong file; dùng2 chữ số thập phân cho lưu lượng/metric,3 chữ số cho NSE nếu hợp lý.

### 20.2. Quy tắc model và checkpoint

- ID cố định: `naive`, `seasonal_naive_365`, `lightgbm_direct`, `gru_direct`.
- Lưu model cùng metadata, feature_order, scaler và lookback; inference phải validate các trường này.
- Không load checkpoint PyTorch không rõ nguồn; chỉ dùng checkpoint do pipeline dự án tạo ra.
- Sau refit, xuất lại dự báo/metrics/figures/JSON từ cùng run; không giữ web JSON cũ.

## 21. Giao diện lệnh cần triển khai

Các lệnh dưới đây là **đặc tả CLI mà agent cần hiện thực**, chưa phải cam kết rằng code tương ứng đã tồn tại trong file kế hoạch. Tất cả đường dẫn tương đối tính từ `code/` trong gốc dự án `ungdungtuan2/`, trừ khi ghi khác.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m pip install --no-deps -e .
python -m colorado_flow.pipeline --config configs/default.yaml --stage audit
python -m colorado_flow.pipeline --config configs/default.yaml --stage eda
python -m colorado_flow.pipeline --config configs/default.yaml --stage features
python -m colorado_flow.pipeline --config configs/default.yaml --stage train
python -m colorado_flow.pipeline --config configs/default.yaml --stage freeze
python -m colorado_flow.pipeline --config configs/default.yaml --stage evaluate
python -m colorado_flow.pipeline --config configs/default.yaml --stage export
python -m pytest tests
```

`train` chỉ dùng Train/Validation; `freeze` ghi cấu hình được chọn và refit; `evaluate` yêu cầu model_selection manifest đã khóa. Có thể bổ sung `--stage all`, nhưng phải giữ các điều kiện này và không tự tuning dựa trên Test.

Chạy website từ `code/web/`:

```bash
npm ci
npm run typecheck
npm run build
npm run preview
```

Biên dịch từ `latex/` nếu máy đã có TeX Live:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
pdfinfo main.pdf
```

Máy hiện tại chưa có `latexmk`/`xelatex`; khi đó upload `latex_overleaf.zip` lên Overleaf, chọn XeLaTeX và `main.tex`, rồi tải PDF về kiểm tra số trang. Agent phải thêm lệnh đóng gói trong `scripts/build_submission.sh` và chạy thử thay vì chỉ mô tả.

## 22. Tiêu chí nghiệm thu chuyên môn và kỹ thuật

| Nhóm | Điều kiện đạt |
|---|---|
| Đề bài (bắt buộc) | Q1/Q2/Q3 đều có kết quả và nhận xét; baseline, 7 bước, 3 metrics đầy đủ |
| Dữ liệu | CSV đúng hash; đủ ngày; không chỉnh đỉnh hoặc bù thiếu không cần thiết |
| Leakage | Scaler đúng Train; feature causal; toàn bộ nhãn không vượt partition; Test không dùng tuning |
| Dự báo | 724 gốc Test đầy đủ cho mỗi model; 7 horizon; thống nhất gốc/ngày mục tiêu |
| Metrics | So sánh cùng mẫu; macro và pooled được tách; NSE đúng công thức và xử lý denominator 0 |
| Cực trị | Q95 thực nghiệm; Z-score rõ; đúng 256 ngày với file hiện tại; không nhầm đợt với ngày |
| Nhận xét | Không áp đặt mùa vụ; không gán nguồn trạm/nhân quả; thừa nhận baseline có thể thắng |
| Website (bổ sung) | Giao diện tiếng Việt, lọc/zoom/tải chạy thật, responsive, không giả live, không có biểu đồ rỗng |
| Báo cáo (bắt buộc) | Đúng tác giả/giảng viên, ≤ 5 trang gồm bìa, hình/bảng dễ đọc, không placeholder |
| Overleaf (bổ sung) | ZIP độc lập, XeLaTeX chạy, font tiếng Việt/citation/asset đúng |
| Tái lập | Config, lockfile, manifest, seed, model, script và README đủ dùng |
| Bàn giao | Bắt buộc: PDF đúng tên. Bổ sung nếu được yêu cầu: ZIP LaTeX, ZIP source, hướng dẫn; kết quả trên web/PDF khớp |

Không áp ngưỡng thành công tùy ý như “NSE phải > 0,9” hoặc “GRU phải thắng”. Thành công là phương pháp đúng, kết quả có thể kiểm chứng và trả lời trung thực đề bài.

## 23. Các rủi ro và cách xử lý đã định trước

| Rủi ro | Cách xử lý |
|---|---|
| PDF vượt 5 trang | Cắt bảng/hình phụ, đưa lên website; không loại bỏ nội dung bắt buộc hoặc dùng font quá nhỏ |
| Mùa vụ yếu hoặc không ổn định | Phân tích detrend, heatmap từng năm; báo đúng, không vẽ kết luận theo kỳ vọng |
| Naive thắng mô hình phức tạp | Kiểm tra leakage/scale; nếu đúng, công bố và diễn giải theo tự tương quan |
| LightGBM kém ở chế độ dòng chảy khác | Thảo luận giới hạn ngoại suy và drift; không thay cấu hình bằng Test |
| GRU dao động theo seed | Seed cố định, mô hình nhỏ, log đầy đủ; nếu thêm nhiều seed, báo phân tán |
| RAM/ổ đĩa hạn chế | Ưu tiên LightGBM/Naive; cài PyTorch CPU-only; giảm batch/hidden_size; dùng Overleaf thay vì cài TeX Live |
| Thiếu thư viện (statsmodels, lightgbm, torch) | Cài theo `requirements.lock.txt`; nếu không cài được, ghi rõ môi trường và dùng phương án thay thế còn kiểm chứng được, không tạo kết quả giả |
| Không publish website được | Bàn giao source + dist + preview command; không ghi URL chưa có vào PDF |
| CSV thiếu metadata trạm | Nêu giới hạn, không dựng tọa độ hoặc tải dataset khác thay thế |
| Không có điểm high-flow trong Test theo Q95_train | Ghi n=0/không đủ mẫu, không tự hạ ngưỡng hoặc tính NSE trên nhóm không có phương sai |
| Thiếu logo/font | Dùng font Overleaf có sẵn; `logo_dhkhtn.jpg` chỉ dùng ở kích thước nhỏ hoặc bỏ; ưu tiên báo cáo biên dịch được và đọc rõ |
| Web/report lệch số | Một pipeline export, cùng manifest, test đối chiếu trước đóng gói |

## 24. Lịch thực hiện và thứ tự ưu tiên

Tổng dự kiến **8–12 ngày công** nếu làm đủ PDF, GRU, website, LaTeX và source. Lộ trình tối thiểu để nộp PDF chỉ khoảng **3–5 ngày**; các phần bổ sung kéo dài thêm. Đây là ước lượng công việc, không phải thời gian train đã đo.

| Chặng | Phạm vi | Mốc bàn giao |
|---|---|---|
| MVP ngày 1–2 | P0–P3 | Audit đúng, cấu trúc, lời giải Q1/Q2 với hình và bảng thật |
| MVP ngày 3–4 | P4–P5, P7 | Split/feature tests, baseline + LightGBM Validation/Test |
| MVP ngày 5 | P10 | PDF ≤ 5 trang, kiểm tra số trang và render |
| Mở rộng ngày 6–8 | P6, P8–P9 | GRU, website với dữ liệu thật |
| Mở rộng ngày 9–10 | P10–P11 | LaTeX/Overleaf ZIP, source ZIP, QA |
| Dự phòng ngày 11–12 | P11 | Sửa lỗi, đóng gói, kiểm tra tái lập |

Đường găng: **đề/giao thức → audit → windows/features → chọn model trên Validation → refit/freeze → Test → export → báo cáo/website cuối → QA**.

Nếu thiếu thời gian, cắt theo thứ tự: interval/bổ sung bootstrap → moving Z phụ → nhiều seed → nhiều fold → chi tiết giao diện phụ. Giữ nguyên Q1/Q2, baseline, ít nhất LightGBM hoặc GRU, dự báo 7 bước, RMSE/MAE/NSE và PDF ≤ 5 trang. Website, LaTeX và source chỉ giữ nếu còn thời gian; không hy sinh nội dung bắt buộc của PDF để làm giao diện.

## 25. Mẫu trạng thái để agent cập nhật

Trong `TASKS.md`, mỗi task có các trường:

```markdown
- Task: P4.7
- Trạng thái: chưa làm / đang làm / hoàn tất / bị chặn
- Input:
- File đã tạo hoặc sửa:
- Lệnh kiểm tra:
- Kết quả kiểm tra:
- Quyết định và lý do:
- Việc tiếp theo:
```

Mỗi phase chỉ đánh dấu hoàn tất khi gate tương ứng đạt. Nếu dừng giữa chừng, ghi lệnh tiếp tục, đường dẫn checkpoint và trạng thái môi trường để agent sau có thể nối tiếp.

## 26. Checklist đối chiếu đề và nghiệm thu nhanh

| Yêu cầu | Bằng chứng tối thiểu | Cách kiểm tra |
|---|---|---|
| Q1 — Trend, Seasonality, chu kỳ năm | Hình xu hướng/mùa vụ; bảng tháng/năm; nhận xét định lượng | Đối chiếu số trong bảng với `results/tables/`; hình có đơn vị và chú giải |
| Q2 — Toàn chuỗi 2010–2023, Z-score/Q95, Top 5% | Hydrograph đủ 14 năm; đường Q95; 256 ngày vượt; danh sách đợt | `extreme_events.csv`, test đếm ngày, hình có highlight |
| Q3a — Chia tập không xáo trộn | 2010–2019 Train, 2020–2021 Validation, 2010–2021 refit, 2022–2023 Test; 724 gốc | `split_manifest.json`, test ngày gốc/nhãn |
| Q3b — Baseline | Naive persistence 7 bước | Bảng metrics có hàng `naive` |
| Q3c — Mô hình 7 bước | LightGBM direct 7 horizon; GRU là mở rộng | `predictions_long.csv`, model/config/checkpoint |
| Q3d — RMSE, MAE, NSE | Theo D+1…D+7, macro 7 horizon và pooled | `metrics_by_horizon.csv`, `metrics_overall.csv` |
| Q4 — PDF ≤ 5 trang | Bìa, nội dung Q1–Q3, bảng/hình, tài liệu tham khảo | `pdfinfo` trả đúng số trang; render toàn bộ |
| U1 — Website (bổ sung) | Build tĩnh, dữ liệu thật, lọc/zoom/tải hoạt động | `npm run build`, kiểm thử luồng chính |
| U2 — LaTeX (bổ sung) | ZIP độc lập, XeLaTeX, asset tương đối | Giải nén thư mục mới và compile |
| U3 — Source (bổ sung) | Code/config/tests/lockfile/README/kết quả demo | Chạy lại pipeline tối thiểu từ checkout sạch |

Không đánh dấu hoàn tất nếu thiếu bằng chứng trong bảng này. Nếu một mục bổ sung bị bỏ, ghi rõ lý do và giới hạn thay vì tạo kết quả hoặc URL giả.

## 27. Lệnh giao việc tổng quát cho agent kế tiếp

> Hãy thực hiện kế hoạch này thành dự án hoàn chỉnh ngay trong thư mục hiện tại `ungdungtuan2/`. Bắt đầu bằng đọc lại bốn tệp tài liệu đầu vào, xác nhận đề và checksum, rồi tạo `code/`, `latex/` và `deliverables/`. Triển khai theo phase và task, kiểm tra tính đúng trước khi hoàn thiện trình bày. Dùng Python cho phân tích, LightGBM direct 7 và GRU direct 7 để so sánh với Naive/Seasonal Naive; chia thời gian, khóa cấu hình bằng Validation và đánh giá Test 2022–2023 đúng giao thức. Huấn luyện trên CPU local; không cần server, không lưu thông tin đăng nhập trong bất kỳ artifact nào. Làm website tương tác bằng dữ liệu thật, bộ LaTeX upload Overleaf và PDF tối đa 5 trang theo phong cách hai báo cáo mẫu. Xuất mọi bảng/hình/JSON từ cùng run; nhận xét như người phân tích dữ liệu có trách nhiệm, nêu bằng chứng và giới hạn. Bàn giao PDF bắt buộc; LaTeX ZIP, source ZIP và hướng dẫn tái lập là hồ sơ bổ sung, không chỉ dừng ở skeleton hoặc một giao diện demo.
