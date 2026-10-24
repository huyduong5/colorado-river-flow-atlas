import { useMemo } from 'react';
import type {
  DailyObservation,
  ExtremesPayload,
  Manifest,
  MetricsPayload,
  PageId,
  SeasonalityPayload,
} from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { EChart } from '../components/EChart';
import { StatCard } from '../components/StatCard';
import { axisStyle, baseOption, COLORS, flowLabel, gridStyle, tooltipStyle } from '../lib/charts';
import { fmtNumber, fmtPercent } from '../lib/format';

interface OverviewPageProps {
  daily: DailyObservation[];
  extremes: ExtremesPayload;
  manifest: Manifest;
  metrics: MetricsPayload;
  seasonality: SeasonalityPayload;
  onNavigate: (page: PageId) => void;
}

export function OverviewPage({
  daily,
  extremes,
  manifest,
  metrics,
  seasonality,
  onNavigate,
}: OverviewPageProps) {
  const stats = useMemo(() => {
    const values = daily.map((row) => row.q);
    const sum = values.reduce((total, value) => total + value, 0);
    const max = values.reduce((best, value) => Math.max(best, value), -Infinity);
    return { mean: sum / values.length, max };
  }, [daily]);

  const testOverall = metrics.overall.filter((row) => row.split === 'test');
  const naive = testOverall.find((row) => row.model === 'naive');
  const bestModel = testOverall.reduce(
    (best, row) => (row.mean_RMSE_7 < best.mean_RMSE_7 ? row : best),
    testOverall[0],
  );

  const option = baseOption({
    grid: { ...gridStyle, top: 24, bottom: 52 },
    tooltip: tooltipStyle,
    xAxis: {
      type: 'time',
      ...axisStyle,
    },
    yAxis: {
      type: 'value',
      name: 'm³/s',
      nameTextStyle: { color: COLORS.muted, fontSize: 11 },
      ...axisStyle,
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      {
        type: 'slider',
        height: 18,
        bottom: 8,
        borderColor: 'transparent',
        backgroundColor: '#eef3f8',
        fillerColor: 'rgba(21, 94, 158, 0.15)',
        handleStyle: { color: COLORS.blue },
        textStyle: { color: COLORS.muted, fontSize: 10 },
      },
    ],
    series: [
      {
        name: 'Lưu lượng ngày',
        type: 'line',
        showSymbol: false,
        sampling: 'lttb',
        data: daily.map((row) => [row.date, row.q]),
        lineStyle: { width: 1.25, color: COLORS.blue },
        itemStyle: { color: COLORS.blue },
        areaStyle: { color: 'rgba(21, 94, 158, 0.08)' },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: COLORS.orange, type: 'dashed', width: 1.2 },
          label: {
            color: COLORS.orange,
            formatter: `Q95 = ${flowLabel(extremes.summary.threshold)}`,
            position: 'insideEndTop',
          },
          data: [{ yAxis: extremes.summary.threshold }],
        },
      },
    ],
  });

  return (
    <div className="page">
      <section className="hero">
        <p className="kicker">Bài tập 2 · Phân tích chuỗi thời gian</p>
        <h1>Một dòng sông, mười bốn năm dữ liệu</h1>
        <p className="hero__lede">
          Từng ngày từ 2010 đến 2023, lưu lượng sông Colorado được ghi lại để trả lời ba câu hỏi:
          chuỗi biến đổi theo xu hướng và mùa vụ nào, những đợt lưu lượng cao nằm ở đâu, và mô hình
          nào dự báo 7 ngày tốt nhất trên giai đoạn Test 2022–2023.
        </p>
        <div className="hero__actions">
          <button className="button button--primary" type="button" onClick={() => onNavigate('forecast')}>
            Xem dự báo 7 ngày
          </button>
          <button className="button button--ghost" type="button" onClick={() => onNavigate('methods')}>
            Đọc phương pháp
          </button>
        </div>
      </section>

      <section className="stat-grid" aria-label="Chỉ số chính">
        <StatCard
          label="Số ngày quan sát"
          value={fmtNumber(daily.length, 0)}
          unit="ngày"
          hint={`${manifest.date_scopes.observations.start.slice(0, 4)}–${manifest.date_scopes.observations.end.slice(0, 4)}`}
          tone="blue"
        />
        <StatCard
          label="Lưu lượng trung bình"
          value={fmtNumber(stats.mean, 2)}
          unit="m³/s"
          hint="Toàn bộ chuỗi 2010–2023"
        />
        <StatCard
          label="Đỉnh lớn nhất"
          value={fmtNumber(stats.max, 2)}
          unit="m³/s"
          hint={`Năm ${extremes.summary.peak_year}`}
          tone="orange"
        />
        <StatCard
          label="Ngưỡng Q95"
          value={fmtNumber(extremes.summary.threshold, 2)}
          unit="m³/s"
          hint={`${extremes.summary.n_days_high} ngày vượt · ${fmtPercent(extremes.summary.share_days_high)}`}
          tone="green"
        />
      </section>

      <ChartPanel
        kicker="Chuỗi ngày"
        title="Lưu lượng sông Colorado, 2010–2023"
        description="Đường cam đánh dấu Q95 tính trên toàn bộ chuỗi. Dữ liệu có các đợt lưu lượng cao rõ rệt, đặc biệt quanh năm 2017."
      >
        <EChart option={option} height="430px" ariaLabel="Biểu đồ lưu lượng ngày của sông Colorado từ 2010 đến 2023" />
      </ChartPanel>

      <section className="insight-grid">
        <article className="insight-card">
          <p className="kicker">Q1 · Xu hướng & mùa vụ</p>
          <h2>Mùa vụ yếu, biến thiên năm lớn</h2>
          <p>
            Dao động trung bình tháng chỉ khoảng {fmtNumber(seasonality.q1.monthly_amplitude_mean)} m³/s,
            trong khi trung bình năm thay đổi hơn {fmtNumber(seasonality.q1.yearly_amplitude_mean)} m³/s.
            Seasonal strength ước lượng là {fmtNumber(seasonality.summary.seasonal_strength, 3)}.
          </p>
          <button className="text-link" type="button" onClick={() => onNavigate('seasonality')}>
            Xem chi tiết Q1
          </button>
        </article>
        <article className="insight-card">
          <p className="kicker">Q2 · Cực trị</p>
          <h2>{extremes.summary.n_events} đợt vượt Q95</h2>
          <p>
            Có {extremes.summary.n_days_high} ngày vượt ngưỡng, chiếm {fmtPercent(extremes.summary.share_days_high)}.
            Đợt dài nhất kéo dài {extremes.summary.longest_event_days} ngày; đỉnh lớn nhất đạt{' '}
            {fmtNumber(extremes.summary.max_event_peak)} m³/s.
          </p>
          <button className="text-link" type="button" onClick={() => onNavigate('extremes')}>
            Xem danh sách đợt
          </button>
        </article>
        <article className="insight-card">
          <p className="kicker">Q3 · Dự báo</p>
          <h2>{bestModel ? manifest.model_labels[bestModel.model] : '—'} nhỉnh nhất</h2>
          <p>
            Trên Test, mean RMSE 7 horizon của mô hình tốt nhất là{' '}
            {bestModel ? fmtNumber(bestModel.mean_RMSE_7) : 'NA'} m³/s. Naive persistence đạt{' '}
            {naive ? fmtNumber(naive.mean_RMSE_7) : 'NA'} m³/s; khác biệt rất nhỏ.
          </p>
          <button className="text-link" type="button" onClick={() => onNavigate('models')}>
            So sánh mô hình
          </button>
        </article>
      </section>

      <aside className="callout callout--note">
        <strong>Đọc kết quả đúng phạm vi.</strong> Đây là backtest trên Test 2022–2023, không phải
        dự báo vận hành, không phải cảnh báo lũ và không dùng để kết luận cho tương lai xa.
      </aside>
    </div>
  );
}
