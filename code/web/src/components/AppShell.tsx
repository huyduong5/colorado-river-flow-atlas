import type { ReactNode } from 'react';
import type { Manifest, PageId } from '../types';
import { fmtDate } from '../lib/format';

const NAV: { id: PageId; label: string; code: string }[] = [
  { id: 'overview', label: 'Tổng quan', code: '00' },
  { id: 'explore', label: 'Khám phá dữ liệu', code: '01' },
  { id: 'seasonality', label: 'Xu hướng & mùa vụ', code: '02' },
  { id: 'extremes', label: 'Cực trị Q95', code: '03' },
  { id: 'forecast', label: 'Dự báo 7 ngày', code: '04' },
  { id: 'models', label: 'So sánh mô hình', code: '05' },
  { id: 'methods', label: 'Phương pháp', code: '06' },
  { id: 'downloads', label: 'Tải về', code: '07' },
];

interface AppShellProps {
  active: PageId;
  onNavigate: (page: PageId) => void;
  manifest: Manifest;
  children: ReactNode;
}

export function AppShell({ active, onNavigate, manifest, children }: AppShellProps) {
  const pdfHref = `${import.meta.env.BASE_URL}downloads/bao_cao.pdf`;

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Bỏ qua điều hướng
      </a>
      <header className="topbar">
        <div className="topbar__brand">
          <span className="brand-mark" aria-hidden="true">
            CR
          </span>
          <div>
            <p className="topbar__eyebrow">Colorado River Flow Atlas</p>
            <p className="topbar__title">Lưu lượng sông Colorado, 2010–2023</p>
          </div>
        </div>
        <div className="topbar__meta">
          <span className="topbar__scope">
            {fmtDate(manifest.date_scopes.observations.start)} –{' '}
            {fmtDate(manifest.date_scopes.observations.end)}
          </span>
          <a className="button button--primary" href={pdfHref} target="_blank" rel="noreferrer">
            PDF báo cáo
          </a>
        </div>
      </header>

      <div className="layout">
        <aside className="sidebar" aria-label="Điều hướng chính">
          <p className="sidebar__label">Nội dung</p>
          <nav className="nav">
            {NAV.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`nav__item${active === item.id ? ' is-active' : ''}`}
                aria-current={active === item.id ? 'page' : undefined}
                onClick={() => onNavigate(item.id)}
              >
                <span className="nav__code">{item.code}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
          <div className="sidebar__note">
            <p className="sidebar__note-title">Phạm vi</p>
            <p>
              Backtest trên Test 2022–2023. Kết quả không phải dự báo vận hành hoặc cảnh báo lũ.
            </p>
            <p className="mono">{manifest.run_id}</p>
          </div>
        </aside>

        <main id="main-content" className="main">
          {children}
          <footer className="footer">
            <p>
              Dữ liệu: <code>colorado_river_flow.csv</code> · Mã băm{' '}
              <span className="mono">{manifest.dataset_hash.slice(0, 12)}…</span>
            </p>
            <p>
              Bài tập 2 · Phân tích chuỗi thời gian · Nguồn số liệu được sử dụng theo đề bài.
            </p>
            <p>
              <a
                href="https://github.com/huyduong5/colorado-river-flow-atlas"
                target="_blank"
                rel="noreferrer"
              >
                Mã nguồn trên GitHub
              </a>
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
