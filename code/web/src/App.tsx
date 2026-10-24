import { useEffect, useState } from 'react';
import type {
  DailyObservation,
  ExtremesPayload,
  HeatmapData,
  Manifest,
  MetricsPayload,
  MonthlyStat,
  PageId,
  SeasonalityPayload,
  YearlyStat,
} from './types';
import { AppShell } from './components/AppShell';
import {
  loadDaily,
  loadExtremes,
  loadHeatmap,
  loadManifest,
  loadMetrics,
  loadMonthly,
  loadSeasonality,
  loadYearly,
} from './lib/api';
import { DownloadsPage } from './pages/DownloadsPage';
import { ExplorePage } from './pages/ExplorePage';
import { ExtremesPage } from './pages/ExtremesPage';
import { ForecastPage } from './pages/ForecastPage';
import { MethodsPage } from './pages/MethodsPage';
import { ModelsPage } from './pages/ModelsPage';
import { OverviewPage } from './pages/OverviewPage';
import { SeasonalityPage } from './pages/SeasonalityPage';

interface CoreData {
  manifest: Manifest;
  daily: DailyObservation[];
  monthly: MonthlyStat[];
  yearly: YearlyStat[];
  heatmap: HeatmapData;
  extremes: ExtremesPayload;
  metrics: MetricsPayload;
  seasonality: SeasonalityPayload;
}

const PAGE_IDS: PageId[] = [
  'overview',
  'explore',
  'seasonality',
  'extremes',
  'forecast',
  'models',
  'methods',
  'downloads',
];

function readPage(): PageId {
  const raw = window.location.hash.replace(/^#\/?/, '');
  return PAGE_IDS.includes(raw as PageId) ? (raw as PageId) : 'overview';
}

export default function App() {
  const [page, setPage] = useState<PageId>(readPage);
  const [data, setData] = useState<CoreData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      loadManifest(),
      loadDaily(),
      loadMonthly(),
      loadYearly(),
      loadHeatmap(),
      loadExtremes(),
      loadMetrics(),
      loadSeasonality(),
    ])
      .then(([manifest, daily, monthly, yearly, heatmap, extremes, metrics, seasonality]) => {
        if (cancelled) return;
        setData({ manifest, daily, monthly, yearly, heatmap, extremes, metrics, seasonality });
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason instanceof Error ? reason.message : 'Không tải được dữ liệu website');
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const onHashChange = () => setPage(readPage());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [page]);

  function navigate(next: PageId) {
    if (next === page) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    window.location.hash = `/${next}`;
    setPage(next);
  }

  if (error) {
    return (
      <div className="boot-screen">
        <div className="boot-card">
          <span className="brand-mark">CR</span>
          <h1>Không tải được Atlas</h1>
          <p>{error}</p>
          <button type="button" className="button button--primary" onClick={() => window.location.reload()}>
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="boot-screen">
        <div className="boot-card">
          <span className="brand-mark">CR</span>
          <p className="kicker">Colorado River Flow Atlas</p>
          <h1>Đang nạp dữ liệu</h1>
          <p>Chuỗi 2010–2023, Q1/Q2/Q3 và kết quả backtest 7 ngày.</p>
          <div className="loading-bar" aria-hidden="true">
            <span />
          </div>
        </div>
      </div>
    );
  }

  let content;
  switch (page) {
    case 'explore':
      content = <ExplorePage daily={data.daily} />;
      break;
    case 'seasonality':
      content = (
        <SeasonalityPage
          monthly={data.monthly}
          yearly={data.yearly}
          heatmap={data.heatmap}
          seasonality={data.seasonality}
        />
      );
      break;
    case 'extremes':
      content = <ExtremesPage daily={data.daily} extremes={data.extremes} />;
      break;
    case 'forecast':
      content = <ForecastPage daily={data.daily} />;
      break;
    case 'models':
      content = <ModelsPage manifest={data.manifest} metrics={data.metrics} onNavigate={navigate} />;
      break;
    case 'methods':
      content = (
        <MethodsPage
          manifest={data.manifest}
          extremes={data.extremes}
          seasonality={data.seasonality}
        />
      );
      break;
    case 'downloads':
      content = <DownloadsPage manifest={data.manifest} />;
      break;
    case 'overview':
    default:
      content = (
        <OverviewPage
          daily={data.daily}
          extremes={data.extremes}
          manifest={data.manifest}
          metrics={data.metrics}
          seasonality={data.seasonality}
          onNavigate={navigate}
        />
      );
  }

  return (
    <AppShell active={page} onNavigate={navigate} manifest={data.manifest}>
      {content}
    </AppShell>
  );
}
