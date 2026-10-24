import { useMemo, useState } from 'react';
import type { DailyObservation, ExtremeEvent, ExtremesPayload } from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { DataTable, type Column } from '../components/DataTable';
import { EChart } from '../components/EChart';
import { axisStyle, baseOption, COLORS, flowLabel, gridStyle, tooltipStyle } from '../lib/charts';
import { fmtDate, fmtNumber, fmtPercent } from '../lib/format';

interface ExtremesPageProps {
  daily: DailyObservation[];
  extremes: ExtremesPayload;
}

export function ExtremesPage({ daily, extremes }: ExtremesPageProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedEvent = extremes.events.find((event) => event.event_id === selectedId) ?? null;

  const chartDaily = useMemo(() => {
    if (!selectedEvent) return daily;
    const start = new Date(`${selectedEvent.start_date}T00:00:00Z`);
    const end = new Date(`${selectedEvent.end_date}T00:00:00Z`);
    start.setUTCDate(start.getUTCDate() - 30);
    end.setUTCDate(end.getUTCDate() + 30);
    const from = start.toISOString().slice(0, 10);
    const to = end.toISOString().slice(0, 10);
    return daily.filter((row) => row.date >= from && row.date <= to);
  }, [daily, selectedEvent]);

  const highDays = useMemo(
    () => chartDaily.filter((row) => row.q > extremes.summary.threshold),
    [chartDaily, extremes.summary.threshold],
  );

  const option = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 28, bottom: 54 },
        tooltip: tooltipStyle,
        legend: {
          top: 0,
          right: 0,
          textStyle: { color: COLORS.muted, fontSize: 11 },
          data: ['Lưu lượng ngày', 'Ngày vượt Q95'],
        },
        xAxis: { type: 'time', ...axisStyle },
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
            fillerColor: 'rgba(194, 65, 12, 0.12)',
            handleStyle: { color: COLORS.orange },
            textStyle: { color: COLORS.muted, fontSize: 10 },
          },
        ],
        series: [
          {
            name: 'Lưu lượng ngày',
            type: 'line',
            showSymbol: false,
            sampling: 'lttb',
            data: chartDaily.map((row) => [row.date, row.q]),
            lineStyle: { width: 1.25, color: COLORS.blue },
            itemStyle: { color: COLORS.blue },
            areaStyle: { color: 'rgba(21, 94, 158, 0.06)' },
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
          {
            name: 'Ngày vượt Q95',
            type: 'scatter',
            data: highDays.map((row) => [row.date, row.q]),
            symbolSize: 7,
            itemStyle: { color: COLORS.red, borderColor: '#ffffff', borderWidth: 1 },
          },
        ],
      }),
    [chartDaily, extremes.summary.threshold, highDays],
  );

  const eventColumns: Column<ExtremeEvent>[] = [
    { key: 'event_id', label: 'Đợt' },
    { key: 'start_date', label: 'Bắt đầu', render: (row) => fmtDate(row.start_date) },
    { key: 'end_date', label: 'Kết thúc', render: (row) => fmtDate(row.end_date) },
    {
      key: 'duration_days',
      label: 'Số ngày',
      align: 'right',
      render: (row) => fmtNumber(row.duration_days, 0),
    },
    {
      key: 'peak_flow',
      label: 'Đỉnh (m³/s)',
      align: 'right',
      render: (row) => fmtNumber(row.peak_flow),
    },
  ];

  const topColumns: Column<ExtremeEvent>[] = [
    {
      key: 'rank',
      label: 'Hạng',
      align: 'center',
      render: (row) => String(row.rank ?? extremes.top5.indexOf(row) + 1),
    },
    { key: 'start_date', label: 'Bắt đầu', render: (row) => fmtDate(row.start_date) },
    { key: 'end_date', label: 'Kết thúc', render: (row) => fmtDate(row.end_date) },
    {
      key: 'duration_days',
      label: 'Số ngày',
      align: 'right',
      render: (row) => fmtNumber(row.duration_days, 0),
    },
    {
      key: 'peak_flow',
      label: 'Đỉnh (m³/s)',
      align: 'right',
      render: (row) => fmtNumber(row.peak_flow),
    },
    { key: 'peak_date', label: 'Ngày đỉnh', render: (row) => fmtDate(row.peak_date) },
  ];

  function toggleEvent(event: ExtremeEvent) {
    setSelectedId((current) => (current === event.event_id ? null : event.event_id));
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Q2 · Top 5% lưu lượng cao</p>
        <h1>Những đợt vượt ngưỡng Q95</h1>
        <p>
          Q95 tính trên toàn bộ chuỗi là {fmtNumber(extremes.summary.threshold)} m³/s. Có{' '}
          {extremes.summary.n_days_high} ngày vượt ngưỡng, gom thành {extremes.summary.n_events} đợt
          liên tiếp. Z tương đương ngưỡng này là {fmtNumber(extremes.summary.z_threshold, 3)}, không
          phải 1,645.
        </p>
      </header>

      <section className="stat-grid stat-grid--compact">
        <article className="mini-stat">
          <span>Ngày vượt Q95</span>
          <strong>{fmtNumber(extremes.summary.n_days_high, 0)}</strong>
          <small>{fmtPercent(extremes.summary.share_days_high)} chuỗi</small>
        </article>
        <article className="mini-stat">
          <span>Số đợt</span>
          <strong>{fmtNumber(extremes.summary.n_events, 0)}</strong>
          <small>Đợt liên tiếp</small>
        </article>
        <article className="mini-stat">
          <span>Đợt dài nhất</span>
          <strong>{fmtNumber(extremes.summary.longest_event_days, 0)} ngày</strong>
          <small>Đếm theo ngày lịch</small>
        </article>
        <article className="mini-stat">
          <span>Đỉnh lớn nhất</span>
          <strong>{fmtNumber(extremes.summary.max_event_peak)} m³/s</strong>
          <small>Năm {extremes.summary.peak_year}</small>
        </article>
      </section>

      <ChartPanel
        kicker="Chuỗi & cực trị"
        title={selectedEvent ? `Đợt ${selectedEvent.event_id}: ${fmtDate(selectedEvent.start_date)} – ${fmtDate(selectedEvent.end_date)}` : 'Toàn bộ chuỗi và các ngày vượt Q95'}
        description={
          selectedEvent
            ? 'Biểu đồ đang phóng to quanh đợt đã chọn, cộng thêm 30 ngày trước và sau. Bấm lại đợt hoặc nút bên phải để xem toàn chuỗi.'
            : 'Điểm đỏ là các ngày có lưu lượng lớn hơn Q95. Chọn một đợt trong bảng để phóng to.'
        }
        actions={
          selectedEvent ? (
            <button type="button" className="button button--ghost button--small" onClick={() => setSelectedId(null)}>
              Xem toàn chuỗi
            </button>
          ) : null
        }
      >
        <EChart option={option} height="410px" ariaLabel="Biểu đồ lưu lượng với các ngày vượt ngưỡng Q95" />
      </ChartPanel>

      <div className="two-column two-column--wide-left">
        <ChartPanel
          kicker="Danh sách"
          title="15 đợt vượt Q95"
          description="Bấm vào một dòng để xem quanh đợt đó. Đợt được xác định theo chuỗi ngày liên tiếp cùng vượt ngưỡng."
        >
          <DataTable
            columns={eventColumns}
            rows={extremes.events}
            rowKey={(row) => row.event_id}
            caption="Danh sách các đợt vượt Q95"
            onRowClick={toggleEvent}
            selectedKey={selectedId}
          />
        </ChartPanel>

        <ChartPanel kicker="Xếp hạng" title="Top 5 đợt theo đỉnh" description="Đỉnh lớn nhất trong mỗi đợt.">
          <DataTable
            columns={topColumns}
            rows={extremes.top5}
            rowKey={(row) => row.event_id}
            caption="Năm đợt có đỉnh lưu lượng lớn nhất"
            onRowClick={toggleEvent}
            selectedKey={selectedId}
          />
        </ChartPanel>
      </div>

      <aside className="callout callout--warning">
        <strong>Lưu ý về ngưỡng.</strong> Q95 được tính trên toàn bộ chuỗi 2010–2023, không tính lại
        theo từng năm. Vì vậy số ngày vượt ngưỡng ở một năm cụ thể có thể cao hơn hoặc thấp hơn 5%.
        Không dùng z &gt; 3 để thay thế cho định nghĩa Top 5%.
      </aside>
    </div>
  );
}
