import type { Manifest } from '../types';
import { fmtDate } from '../lib/format';

interface DownloadsPageProps {
  manifest: Manifest;
}

interface DownloadItem {
  label: string;
  file: string;
  note: string;
  kind: 'PDF' | 'ZIP' | 'CSV' | 'JSON';
}

export function DownloadsPage({ manifest }: DownloadsPageProps) {
  const base = import.meta.env.BASE_URL;
  const items: DownloadItem[] = [
    {
      label: 'Báo cáo PDF',
      file: 'downloads/bao_cao.pdf',
      note: 'Bản nộp chính, tối đa 5 trang, có Q1–Q3 và kết luận.',
      kind: 'PDF',
    },
    {
      label: 'Source code',
      file: 'downloads/source_code.zip',
      note: 'Toàn bộ pipeline, cấu hình, test, dữ liệu đã xử lý và website.',
      kind: 'ZIP',
    },
    {
      label: 'Gói Overleaf',
      file: 'downloads/latex_overleaf.zip',
      note: 'Mã nguồn LaTeX, hình, bảng và tài liệu hướng dẫn biên dịch.',
      kind: 'ZIP',
    },
    {
      label: 'Dự báo dài',
      file: 'downloads/predictions_long.csv',
      note: '5.068 cặp dự báo Test của Naive, LightGBM và Seasonal Naive.',
      kind: 'CSV',
    },
    {
      label: 'Chỉ số tổng hợp',
      file: 'downloads/metrics_overall.csv',
      note: 'RMSE, MAE, NSE theo mô hình trên Validation/Test.',
      kind: 'CSV',
    },
    {
      label: 'Chỉ số theo horizon',
      file: 'downloads/metrics_by_horizon.csv',
      note: 'RMSE, MAE, NSE cho D+1 đến D+7.',
      kind: 'CSV',
    },
    {
      label: 'Danh sách đợt cực trị',
      file: 'downloads/extreme_events.csv',
      note: '15 đợt vượt Q95, độ dài, đỉnh và ngày đỉnh.',
      kind: 'CSV',
    },
    {
      label: 'Chuỗi đã xử lý',
      file: 'downloads/colorado_river_flow_processed.csv',
      note: 'Chuỗi ngày 2010–2023 dùng trong toàn bộ phân tích.',
      kind: 'CSV',
    },
    {
      label: 'Manifest dữ liệu web',
      file: 'data/manifest.json',
      note: 'Run ID, mã băm dữ liệu, phạm vi và định nghĩa ngưỡng.',
      kind: 'JSON',
    },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Hồ sơ</p>
        <h1>Tải báo cáo và dữ liệu</h1>
        <p>
          Bản PDF là sản phẩm nộp bắt buộc. Source code, gói LaTeX và các tệp CSV/JSON là hồ sơ bổ
          sung để kiểm tra và tái lập kết quả.
        </p>
      </header>

      <section className="download-meta">
        <div>
          <span>Run ID</span>
          <strong className="mono">{manifest.run_id}</strong>
        </div>
        <div>
          <span>Dữ liệu</span>
          <strong>
            {fmtDate(manifest.date_scopes.observations.start)} –{' '}
            {fmtDate(manifest.date_scopes.observations.end)}
          </strong>
        </div>
        <div>
          <span>Test</span>
          <strong>{fmtDate(manifest.date_scopes.test.start)} – {fmtDate(manifest.date_scopes.test.end)}</strong>
        </div>
        <div>
          <span>SHA256</span>
          <strong className="mono">{manifest.dataset_hash.slice(0, 20)}…</strong>
        </div>
      </section>

      <div className="download-grid">
        {items.map((item) => (
          <a
            key={item.file}
            className="download-card"
            href={`${base}${item.file}`}
            download
          >
            <span className={`file-badge file-badge--${item.kind.toLowerCase()}`}>{item.kind}</span>
            <span className="download-card__body">
              <strong>{item.label}</strong>
              <span>{item.note}</span>
              <code>{item.file}</code>
            </span>
          </a>
        ))}
      </div>

      <aside className="callout">
        <strong>Ghi chú.</strong> Nếu một liên kết chưa có trong bản đang chạy, đó là do bản đóng gói
        chưa được tạo. Chạy <span className="mono">pipeline --stage all</span> và script đóng gói để
        sinh đầy đủ PDF/ZIP/CSV. Không có kết quả mô hình nào được tạo thủ công.
      </aside>
    </div>
  );
}
