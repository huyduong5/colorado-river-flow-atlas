import { useMemo, useState } from 'react';
import type { DailyObservation } from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { DataTable, type Column } from '../components/DataTable';
import { EChart } from '../components/EChart';
import { axisStyle, baseOption, COLORS, gridStyle, tooltipStyle } from '../lib/charts';
import { downloadCsv, fmtDate, fmtNumber } from '../lib/format';

interface ExplorePageProps {
  daily: DailyObservation[];
}

export function ExplorePage({ daily }: ExplorePageProps) {
  const minDate = daily[0]?.date ?? '';
  const maxDate = daily[daily.length - 1]?.date ?? '';
  const [start, setStart] = useState('2015-01-01');
  const [end, setEnd] = useState(maxDate);

  const filtered = useMemo(
    () => daily.filter((row) => row.date >= start && row.date <= end),
    [daily, start, end],
  );

  const stats = useMemo(() => {
    if (filtered.length === 0) return null;
    const values = filtered.map((row) => row.q);
    return {
      count: filtered.length,
      mean: values.reduce((total, value) => total + value, 0) / values.length,
      max: Math.max(...values),
      min: Math.min(...values),
    };
  }, [filtered]);

  const option = baseOption({
    grid: { ...gridStyle, top: 24, bottom: 58 },
    tooltip: tooltipStyle,
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
        fillerColor: 'rgba(14, 116, 144, 0.15)',
        handleStyle: { color: COLORS.cyan },
        textStyle: { color: COLORS.muted, fontSize: 10 },
      },
    ],
    series: [
      {
        name: 'Lưu lượng ngày',
        type: 'line',
        showSymbol: false,
        sampling: 'lttb',
        data: filtered.map((row) => [row.date, row.q]),
        lineStyle: { width: 1.4, color: COLORS.cyan },
        itemStyle: { color: COLORS.cyan },
        areaStyle: { color: 'rgba(14, 116, 144, 0.08)' },
      },
    ],
  });

  const columns: Column<DailyObservation>[] = [
    { key: 'date', label: 'Ngày', render: (row) => fmtDate(row.date) },
    {
      key: 'q',
      label: 'Lưu lượng (m³/s)',
      align: 'right',
      render: (row) => fmtNumber(row.q),
    },
  ];

  const rowsToShow = filtered.slice(-20).reverse();

  function exportCsv() {
    downloadCsv('colorado_river_flow_filtered.csv', [
      ['date', 'discharge_m3s'],
      ...filtered.map((row) => [row.date, String(row.q)]),
    ]);
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Q0 · Dữ liệu</p>
        <h1>Khám phá chuỗi lưu lượng</h1>
        <p>
          Lọc theo khoảng ngày, xem biểu đồ và tải lại đúng khoảng đã chọn. Đơn vị lưu lượng là
          m³/s; chuỗi gốc có {fmtNumber(daily.length, 0)} quan sát ngày.
        </p>
      </header>

      <section className="filter-bar" aria-label="Bộ lọc khoảng ngày">
        <label>
          Từ ngày
          <input
            type="date"
            value={start}
            min={minDate}
            max={maxDate}
            onChange={(event) => setStart(event.target.value || minDate)}
          />
        </label>
        <label>
          Đến ngày
          <input
            type="date"
            value={end}
            min={minDate}
            max={maxDate}
            onChange={(event) => setEnd(event.target.value || maxDate)}
          />
        </label>
        <div className="filter-bar__quick">
          <button type="button" className="chip" onClick={() => setStart('2010-01-01')}>
            Toàn chuỗi
          </button>
          <button type="button" className="chip" onClick={() => setStart('2015-01-01')}>
            2015–2023
          </button>
          <button type="button" className="chip" onClick={() => setStart('2022-01-01')}>
            Test 2022–2023
          </button>
          <button type="button" className="button button--ghost button--small" onClick={exportCsv}>
            Tải CSV đoạn đang xem
          </button>
        </div>
      </section>

      <section className="stat-grid stat-grid--compact">
        <article className="mini-stat">
          <span>Số ngày</span>
          <strong>{stats ? fmtNumber(stats.count, 0) : '0'}</strong>
        </article>
        <article className="mini-stat">
          <span>Trung bình</span>
          <strong>{stats ? `${fmtNumber(stats.mean)} m³/s` : 'NA'}</strong>
        </article>
        <article className="mini-stat">
          <span>Nhỏ nhất</span>
          <strong>{stats ? `${fmtNumber(stats.min)} m³/s` : 'NA'}</strong>
        </article>
        <article className="mini-stat">
          <span>Lớn nhất</span>
          <strong>{stats ? `${fmtNumber(stats.max)} m³/s` : 'NA'}</strong>
        </article>
      </section>

      <ChartPanel
        kicker="Chuỗi đã lọc"
        title="Diễn biến lưu lượng theo ngày"
        description="Dùng thanh trượt bên dưới để phóng to. Biểu đồ lấy mẫu LTTB khi hiển thị để giữ hiệu năng, nhưng bảng và CSV dùng đúng dữ liệu gốc."
      >
        <EChart option={option} height="420px" ariaLabel="Biểu đồ lưu lượng theo khoảng ngày đã chọn" />
      </ChartPanel>

      <ChartPanel
        kicker="Bảng dữ liệu"
        title="20 ngày gần nhất trong khoảng lọc"
        description="Sắp xếp mới nhất trước. Tải CSV để lấy toàn bộ khoảng đang chọn."
      >
        <DataTable
          columns={columns}
          rows={rowsToShow}
          rowKey={(row) => row.date}
          caption="20 quan sát gần nhất trong khoảng ngày đã chọn"
          emptyMessage="Khoảng ngày không có dữ liệu. Hãy chọn lại."
        />
      </ChartPanel>
    </div>
  );
}
