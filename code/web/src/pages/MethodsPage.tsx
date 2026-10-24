import type { ExtremesPayload, Manifest, SeasonalityPayload } from '../types';
import { fmtNumber } from '../lib/format';

interface MethodsPageProps {
  manifest: Manifest;
  extremes: ExtremesPayload;
  seasonality: SeasonalityPayload;
}

export function MethodsPage({ manifest, extremes, seasonality }: MethodsPageProps) {
  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Phương pháp</p>
        <h1>Cách đọc những con số phía sau</h1>
        <p>
          Trang này tóm tắt quy trình để người đọc kiểm tra tính hợp lý của kết quả: dữ liệu nào
          được dùng, chia tập ra sao, đặc trưng có gây rò rỉ không, và các chỉ số được tính thế nào.
        </p>
      </header>

      <div className="prose-grid">
        <section>
          <h2>1. Dữ liệu và kiểm định</h2>
          <p>
            Chuỗi gốc có 5.113 quan sát ngày, từ 01/01/2010 đến 31/12/2023, không thiếu ngày, không
            trùng ngày và không có giá trị lưu lượng thiếu. Mã băm SHA256 của tệp gốc là{' '}
            <span className="mono">{manifest.dataset_hash}</span>.
          </p>
          <p>
            Q95 được tính trên toàn bộ chuỗi bằng quantile tuyến tính, không tính lại theo từng năm.
            Với dữ liệu hiện tại, Q95 = {fmtNumber(extremes.summary.threshold)} m³/s và Z tương đương
            là {fmtNumber(extremes.summary.z_threshold, 3)}. Vì vậy phát biểu “Z &gt; 3 là Top 5%” là
            sai với chuỗi này.
          </p>
        </section>

        <section>
          <h2>2. Chia Train / Validation / Test</h2>
          <p>
            Không xáo trộn dữ liệu. Train dùng 2010–2019, Validation dùng 2020–2021, Test dùng
            2022–2023. Mỗi ngày gốc trong Validation/Test tạo 7 cặp dự báo D+1…D+7; cửa sổ mục tiêu
            không vượt khỏi tập tương ứng.
          </p>
          <p>
            Theo manifest hiện tại: 3.615 ngày gốc Train, 725 ngày gốc Validation, 724 ngày gốc Test
            (5.068 cặp), và 4.346 ngày gốc Refit sau khi chọn mô hình. Các mốc ngày được kiểm tra tự
            động trong test.
          </p>
        </section>

        <section>
          <h2>3. Đặc trưng của LightGBM</h2>
          <p>
            Mỗi ngày gốc dùng lag 1, 2, 3, 7, 14, 28 ngày; trung bình và độ lệch chuẩn trượt 7, 14,
            30, 90 ngày; biến lịch sin/cos của ngày trong năm và tháng; cùng các biến lịch của ngày
            mục tiêu. Tất cả đặc trưng chỉ dùng dữ liệu đến ngày gốc.
          </p>
          <p>
            LightGBM được huấn luyện trực tiếp cho từng horizon. Với cấu hình hiện tại, mục tiêu là
            chênh lệch <span className="mono">q(t+h) − q(t)</span>; dự báo cuối cùng cộng lại vào
            lưu lượng ngày gốc. Cách này ổn định hơn với chuỗi có mức nền thay đổi mạnh, nhưng vẫn
            là mô hình direct 7 horizon.
          </p>
        </section>

        <section>
          <h2>4. Baseline và lựa chọn mô hình</h2>
          <p>
            Naive persistence dùng <span className="mono">ŷ(t+h) = y(t)</span>. Seasonal Naive 365
            dùng giá trị cùng ngày của năm trước. LightGBM được tìm siêu tham số trên Validation;
            Test không được dùng để chọn mô hình.
          </p>
          <p>
            Kết quả Validation: Naive mean RMSE 5,535; LightGBM delta 5,569; Seasonal Naive 65,57.
            Kết quả Test: Naive 5,308; LightGBM 5,329; Seasonal Naive 60,48. Khác biệt giữa Naive và
            LightGBM rất nhỏ, và Naive nhỉnh hơn trên Test.
          </p>
        </section>

        <section>
          <h2>5. Chỉ số đánh giá</h2>
          <p>
            Với mỗi horizon và mỗi ngày gốc, tính RMSE, MAE và NSE giữa dự báo và thực tế. Mean
            RMSE/MAE/NSE là trung bình trên 7 horizon; pooled RMSE/MAE/NSE tính trên toàn bộ cặp dự
            báo, không lấy trung bình các chỉ số.
          </p>
          <pre>
{`RMSE = sqrt(mean((y - ŷ)^2))
MAE  = mean(|y - ŷ|)
NSE  = 1 - sum((y - ŷ)^2) / sum((y - mean(y))^2)`}
          </pre>
          <p>
            NSE = 1 là hoàn hảo; NSE = 0 tương đương dự báo bằng trung bình; NSE âm là kém hơn mức
            trung bình. Seasonal Naive 365 có NSE âm rất lớn trên Test vì chuỗi không lặp lại ổn định
            theo năm.
          </p>
        </section>

        <section>
          <h2>6. Q1 và Q2</h2>
          <p>
            Q1 dùng trung bình tháng/năm, STL chu kỳ 365 ngày và ACF. Seasonal strength hiện tại là{' '}
            {fmtNumber(seasonality.summary.seasonal_strength, 3)}; trend strength là{' '}
            {fmtNumber(seasonality.summary.trend_strength, 3)}. Vì vậy mùa vụ yếu, không nên suy diễn
            một chu kỳ tháng mạnh.
          </p>
          <p>
            Q2 xác định các ngày vượt Q95, gộp các ngày liên tiếp thành đợt, đếm độ dài và đỉnh. Có{' '}
            {extremes.summary.n_events} đợt; đợt dài nhất {extremes.summary.longest_event_days} ngày;
            đỉnh lớn nhất {fmtNumber(extremes.summary.max_event_peak)} m³/s.
          </p>
        </section>

        <section>
          <h2>7. Giới hạn</h2>
          <ul>
            <li>Chỉ có 14 năm dữ liệu ngày; Test chỉ 2 năm, chưa đủ để kết luận dài hạn.</li>
            <li>Chưa có biến ngoại sinh như mưa, nhiệt độ, tuyết tan hoặc vận hành hồ chứa.</li>
            <li>GRU chưa chạy trong môi trường hiện tại; không có kết quả GRU để báo cáo.</li>
            <li>Kết quả là backtest, không phải dự báo vận hành hoặc cảnh báo lũ.</li>
            <li>LightGBM delta là lựa chọn kỹ thuật đã ghi rõ, không phải kết quả được chọn theo Test.</li>
          </ul>
        </section>

        <section>
          <h2>8. Tái lập</h2>
          <p>Từ thư mục gốc dự án, chạy pipeline trong môi trường ảo đã khóa phiên bản:</p>
          <pre>
{`cd code
.venv/bin/python -m pytest -q
.venv/bin/python -m colorado_flow.pipeline --stage all`}
          </pre>
          <p>
            Website đọc dữ liệu đã xuất trong <span className="mono">web/public/data</span>. Tệp
            nguồn, LaTeX và dữ liệu trung gian nằm trong gói source; xem trang Tải về.
          </p>
        </section>
      </div>
    </div>
  );
}
