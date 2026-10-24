import { useEffect, useMemo, useState } from 'react';
import type { DailyObservation, ForecastRow, PredictionsPayload } from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { DataTable, type Column } from '../components/DataTable';
import { EChart } from '../components/EChart';
import { loadPredictions } from '../lib/api';
import { axisStyle, baseOption, COLORS, gridStyle, tooltipStyle } from '../lib/charts';
import { fmtDate, fmtNumber } from '../lib/format';

interface ForecastPageProps {
  daily: DailyObservation[];
}

interface ForecastTableRow extends ForecastRow {
  absError: number | null;
}

export function ForecastPage({ daily }: ForecastPageProps) {
  const [payload, setPayload] = useState<PredictionsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [model, setModel] = useState('lightgbm_direct');
  const [origin, setOrigin] = useState('');
  const [showActual, setShowActual] = useState(true);

  useEffect(() => {
    let cancelled = false;
    loadPredictions()
      .then((data) => {
        if (cancelled) return;
        setPayload(data);
        const origins = [...new Set(data.rows.map((row) => row.origin_date.slice(0, 10)))].sort();
        setOrigin(origins[origins.length - 1] ?? '');
        if (!data.models.includes(model) && data.models.length > 0) {
          setModel(data.models.includes('lightgbm_direct') ? 'lightgbm_direct' : data.models[0]);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) setError(reason instanceof Error ? reason.message : 'Không tải được dự báo');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const rows = useMemo(() => {
    if (!payload) return [];
    return payload.rows
      .filter((row) => row.model === model && row.origin_date.slice(0, 10) === origin)
      .sort((a, b) => a.horizon - b.horizon);
  }, [model, origin, payload]);

  const origins = useMemo(
    () => (payload ? [...new Set(payload.rows.map((row) => row.origin_date.slice(0, 10)))].sort() : []),
    [payload],
  );

  const history = useMemo(() => {
    if (!origin) return [];
    const originDate = new Date(`${origin}T00:00:00Z`);
    const start = new Date(originDate);
    start.setUTCDate(start.getUTCDate() - 60);
    const from = start.toISOString().slice(0, 10);
    return daily.filter((row) => row.date >= from && row.date <= origin);
  }, [daily, origin]);

  const stats = useMemo(() => {
    const withTruth = rows.filter((row) => row.y_true !== null);
    if (withTruth.length === 0) return null;
    const errors = withTruth.map((row) => (row.y_pred - (row.y_true as number)) ** 2);
    const absErrors = withTruth.map((row) => Math.abs(row.y_pred - (row.y_true as number)));
    return {
      rmse: Math.sqrt(errors.reduce((total, value) => total + value, 0) / errors.length),
      mae: absErrors.reduce((total, value) => total + value, 0) / absErrors.length,
    };
  }, [rows]);

  const option = useMemo(() => {
    const originPoint = history[history.length - 1];
    const forecastData: [string, number][] = originPoint
      ? [[originPoint.date, originPoint.q], ...rows.map((row) => [row.target_date, row.y_pred] as [string, number])]
      : rows.map((row) => [row.target_date, row.y_pred] as [string, number]);
    const actualData: [string, number][] = originPoint
      ? [
          [originPoint.date, originPoint.q],
          ...rows
            .filter((row) => row.y_true !== null)
            .map((row) => [row.target_date, row.y_true as number] as [string, number]),
        ]
      : [];

    return baseOption({
      grid: { ...gridStyle, top: 40, bottom: 62 },
      tooltip: tooltipStyle,
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        {
          type: 'slider',
          height: 16,
          bottom: 6,
          borderColor: 'transparent',
          backgroundColor: '#eef3f8',
          fillerColor: 'rgba(14, 116, 144, 0.15)',
          handleStyle: { color: COLORS.cyan },
          textStyle: { color: COLORS.muted, fontSize: 9 },
        },
      ],
      legend: {
        top: 0,
        right: 0,
        textStyle: { color: COLORS.muted, fontSize: 11 },
        data: ['Lịch sử', 'Dự báo', 'Thực tế'],
      },
      xAxis: { type: 'time', ...axisStyle },
      yAxis: {
        type: 'value',
        scale: true,
        name: 'm³/s',
        nameTextStyle: { color: COLORS.muted, fontSize: 11 },
        ...axisStyle,
      },
      series: [
        {
          name: 'Lịch sử',
          type: 'line',
          showSymbol: false,
          data: history.map((row) => [row.date, row.q]),
          lineStyle: { width: 1.8, color: COLORS.blue },
          itemStyle: { color: COLORS.blue },
        },
        {
          name: 'Dự báo',
          type: 'line',
          data: forecastData,
          symbol: 'circle',
          symbolSize: 5,
          lineStyle: { width: 2.2, color: COLORS.orange, type: 'dashed' },
          itemStyle: { color: COLORS.orange },
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { color: '#94a3b8', type: 'dotted', width: 1 },
            label: { color: COLORS.muted, formatter: 'Ngày gốc', fontSize: 10 },
            data: [{ xAxis: origin }],
          },
        },
        ...(showActual && actualData.length > 0
          ? [
              {
                name: 'Thực tế',
                type: 'line' as const,
                data: actualData,
                symbol: 'circle',
                symbolSize: 4,
                lineStyle: { width: 1.6, color: COLORS.green },
                itemStyle: { color: COLORS.green },
              },
            ]
          : []),
      ],
    });
  }, [history, origin, rows, showActual]);

  const tableRows: ForecastTableRow[] = rows.map((row) => ({
    ...row,
    absError: row.y_true === null ? null : Math.abs(row.y_pred - row.y_true),
  }));

  const columns: Column<ForecastTableRow>[] = [
    { key: 'horizon', label: 'D+', align: 'center', render: (row) => String(row.horizon) },
    { key: 'target_date', label: 'Ngày mục tiêu', render: (row) => fmtDate(row.target_date) },
    {
      key: 'y_pred',
      label: 'Dự báo (m³/s)',
      align: 'right',
      render: (row) => fmtNumber(row.y_pred),
    },
    {
      key: 'y_true',
      label: 'Thực tế (m³/s)',
      align: 'right',
      render: (row) => (row.y_true === null ? 'NA' : fmtNumber(row.y_true)),
    },
    {
      key: 'absError',
      label: 'Sai số tuyệt đối',
      align: 'right',
      render: (row) => (row.absError === null ? 'NA' : fmtNumber(row.absError)),
    },
  ];

  if (error) {
    return (
      <div className="page">
        <header className="page-header">
          <p className="kicker">Q3 · Dự báo</p>
          <h1>Dự báo 7 ngày</h1>
        </header>
        <p className="empty-state">{error}</p>
      </div>
    );
  }

  if (!payload) {
    return (
      <div className="page">
        <header className="page-header">
          <p className="kicker">Q3 · Dự báo</p>
          <h1>Dự báo 7 ngày</h1>
        </header>
        <p className="loading-state">Đang tải kết quả backtest…</p>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Q3 · Dự báo 7 ngày</p>
        <h1>Chọn một ngày gốc, xem 7 ngày tiếp theo</h1>
        <p>
          Mỗi điểm là một lần dự báo 7 ngày được tạo từ dữ liệu chỉ đến ngày gốc. Đây là backtest
          trên Test 2022–2023, không phải dự báo trực tiếp cho tương lai.
        </p>
      </header>

      <section className="filter-bar filter-bar--forecast" aria-label="Chọn mô hình và ngày gốc">
        <label>
          Mô hình
          <select value={model} onChange={(event) => setModel(event.target.value)}>
            {payload.models.map((item) => (
              <option key={item} value={item}>
                {payload.labels[item] ?? item}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ngày gốc
          <select value={origin} onChange={(event) => setOrigin(event.target.value)}>
            {origins.map((item) => (
              <option key={item} value={item}>
                {fmtDate(item)}
              </option>
            ))}
          </select>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showActual}
            onChange={(event) => setShowActual(event.target.checked)}
          />
          Hiện giá trị thực tế
        </label>
      </section>

      <section className="stat-grid stat-grid--compact">
        <article className="mini-stat">
          <span>RMSE 7 ngày tại điểm gốc</span>
          <strong>{stats ? `${fmtNumber(stats.rmse)} m³/s` : 'NA'}</strong>
        </article>
        <article className="mini-stat">
          <span>MAE 7 ngày tại điểm gốc</span>
          <strong>{stats ? `${fmtNumber(stats.mae)} m³/s` : 'NA'}</strong>
        </article>
        <article className="mini-stat">
          <span>Lưu lượng ngày gốc</span>
          <strong>
            {history.length > 0 ? `${fmtNumber(history[history.length - 1].q)} m³/s` : 'NA'}
          </strong>
        </article>
        <article className="mini-stat">
          <span>Dải dự báo</span>
          <strong>D+1 → D+7</strong>
        </article>
      </section>

      <ChartPanel
        kicker="Đường dự báo"
        title={`${payload.labels[model] ?? model} · gốc ${fmtDate(origin)}`}
        description="Đường liền là 60 ngày lịch sử; đường nét đứt là 7 ngày dự báo; đường xanh là giá trị thực tế của các ngày mục tiêu."
      >
        <EChart option={option} height="430px" ariaLabel="Biểu đồ lịch sử và dự báo 7 ngày tại ngày gốc đã chọn" />
      </ChartPanel>

      <ChartPanel
        kicker="Bảng dự báo"
        title="Chi tiết 7 ngày"
        description="Sai số tuyệt đối = |dự báo − thực tế|. Các giá trị thực tế lấy từ chuỗi gốc, không được dùng làm feature."
      >
        <DataTable
          columns={columns}
          rows={tableRows}
          rowKey={(row) => `${row.model}-${row.origin_date}-${row.horizon}`}
          caption="Bảng dự báo 7 ngày cho ngày gốc đã chọn"
        />
      </ChartPanel>

      <aside className="callout callout--note">
        <strong>Không chọn mô hình bằng Test.</strong> Mô hình và siêu tham số được chọn trên
        Validation 2020–2021; Test 2022–2023 chỉ dùng để báo cáo. Ở cấp độ toàn bộ Test, Naive
        persistence có mean RMSE thấp hơn LightGBM một chút.
      </aside>
    </div>
  );
}
