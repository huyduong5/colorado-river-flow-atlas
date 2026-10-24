# Tham chiếu thiết kế và phương pháp

Khảo sát ngày 24/10/2026. Chỉ dùng để tham khảo cách tổ chức thông tin; không sao chép
giao diện, logo hoặc nội dung.

| Nguồn | URL | Phần vận dụng |
|---|---|---|
| USGS Water Data for the Nation | https://waterdata.usgs.gov/ | Cách tổ chức tra cứu chuỗi, biểu đồ và tải dữ liệu |
| USGS Explore Water Data | https://waterdata.usgs.gov/explore/ | Bộ lọc, luồng khám phá dữ liệu lịch sử |
| USGS giới thiệu giao diện dữ liệu | https://waterdata.usgs.gov/blog/wdfn-updates-2025/ | Kết nối graph, table và ngữ cảnh thống kê |
| NOAA National Water Prediction Service | https://water.noaa.gov/ | Phân biệt đoạn quan trắc và đoạn dự báo trên hydrograph |
| NOAA giới thiệu NWPS | https://www.noaa.gov/news-release/national-weather-service-launches-new-website-for-water-prediction-and-products | Ý tưởng trình bày sản phẩm dự báo thủy văn |
| Apache ECharts gallery | https://echarts.apache.org/examples/en/index.html | Line/area, boxplot, heatmap, zoom và tooltip |
| scikit-learn TimeSeriesSplit | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html | Kiểm chứng chia tập theo thời gian và gap |
| statsmodels STL | https://www.statsmodels.org/stable/examples/notebooks/generated/stl_decomposition.html | Cơ sở triển khai phân rã xu hướng/mùa vụ |
| LightGBM parameters | https://lightgbm.readthedocs.io/en/stable/Parameters.html | Chọn và ghi cấu hình mô hình |
| PyTorch GRU | https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html | Tham khảo shape/tham số GRU (chưa chạy) |
| Nash và Sutcliffe, 1970 | https://www.sciencedirect.com/science/article/pii/0022169470902556 | Định nghĩa NSE, DOI `10.1016/0022-1694(70)90255-6` |

## Thiết kế đã dùng

- Báo cáo: bố cục học thuật gọn, chữ 12pt, lề 2cm, bảng `booktabs`, hình vector, chú
  thích ngắn; không chèn logo lớn.
- Website: nền sáng, tiêu đề serif, màu navy/blue là chính, cam/đỏ cho cực trị; bảng và
  biểu đồ ưu tiên khả năng đọc; có trạng thái loading/error, điều hướng bàn phím và
  responsive.
- Không dựng bản đồ trạm hoặc URL công khai khi chưa có dữ liệu/kiểm chứng.
- Logo trường lấy từ tệp đề bài, chỉ dùng nhỏ trên bìa PDF.
