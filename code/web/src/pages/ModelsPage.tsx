import { useMemo } from 'react';
import type { Manifest, MetricHorizon, MetricOverall, MetricYear, MetricsPayload, PageId } from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { DataTable, type Column } from '../components/DataTable';
import { EChart } from '../components/EChart';
import { axisStyle, baseOption, COLORS, gridStyle, tooltipStyle } from '../lib/charts';
import { fmtNumber } from '../lib/format';

interface ModelsPageProps {
  manifest: Manifest;
  metrics: MetricsPayload;
  onNavigate: (page: PageId) => void;
}

const MODEL_ORDER = ['naive', 'lightgbm_direct', 'seasonal_naive_365'];

export function ModelsPage({ manifest, metrics, onNavigate }: ModelsPageProps) {
  const testOverall = useMemo(
    () =>
      [...metrics.overall]
        .filter((row) => row.split === 'test')
        .sort((a, b) => MODEL_ORDER.indexOf(a.model) - MODEL_ORDER.indexOf(b.model)),
    [metrics.overall],
  );

  const testHorizon = useMemo(
    () =>
      metrics.by_horizon.filter(
        (row) => row.split === 'test' && ['naive', 'lightgbm_direct'].includes(row.model),
      ),
    [metrics.by_horizon],
  );

  const rmseOption = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 38, bottom: 36 },
        tooltip: tooltipStyle,
        legend: {
          top: 0,
          right: 0,
          textStyle: { color: COLORS.muted, fontSize: 11 },
          data: ['Naive persistence', 'LightGBM direct 7'],
        },
        xAxis: {
          type: 'category',
          data: ['D+1', 'D+2', 'D+3', 'D+4', 'D+5', 'D+6', 'D+7'],
          ...axisStyle,
        },
        yAxis: {
          type: 'value',
          name: 'RMSE (m³/s)',
          nameTextStyle: { color: COLORS.muted, fontSize: 11 },
          ...axisStyle,
        },
        series: [
          {
            name: 'Naive persistence',
            type: 'line',
            data: [1, 2, 3, 4, 5, 6, 7].map(
              (h) => testHorizon.find((row) => row.model === 'naive' && row.horizon === h)?.RMSE ?? null,
            ),
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2, color: COLORS.muted },
            itemStyle: { color: COLORS.muted },
          },
          {
            name: 'LightGBM direct 7',
            type: 'line',
            data: [1, 2, 3, 4, 5, 6, 7].map(
              (h) =>
                testHorizon.find((row) => row.model === 'lightgbm_direct' && row.horizon === h)?.RMSE ?? null,
            ),
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2.2, color: COLORS.orange },
            itemStyle: { color: COLORS.orange },
          },
        ],
      }),
    [testHorizon],
  );

  const nseOption = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 38, bottom: 36 },
        tooltip: tooltipStyle,
        legend: {
          top: 0,
          right: 0,
          textStyle: { color: COLORS.muted, fontSize: 11 },
          data: ['Naive persistence', 'LightGBM direct 7'],
        },
        xAxis: {
          type: 'category',
          data: ['D+1', 'D+2', 'D+3', 'D+4', 'D+5', 'D+6', 'D+7'],
          ...axisStyle,
        },
        yAxis: {
          type: 'value',
          name: 'NSE',
          min: 0.75,
          max: 1,
          nameTextStyle: { color: COLORS.muted, fontSize: 11 },
          ...axisStyle,
        },
        series: [
          {
            name: 'Naive persistence',
            type: 'line',
            data: [1, 2, 3, 4, 5, 6, 7].map(
              (h) => testHorizon.find((row) => row.model === 'naive' && row.horizon === h)?.NSE ?? null,
            ),
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2, color: COLORS.muted },
            itemStyle: { color: COLORS.muted },
          },
          {
            name: 'LightGBM direct 7',
            type: 'line',
            data: [1, 2, 3, 4, 5, 6, 7].map(
              (h) =>
                testHorizon.find((row) => row.model === 'lightgbm_direct' && row.horizon === h)?.NSE ?? null,
            ),
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2.2, color: COLORS.orange },
            itemStyle: { color: COLORS.orange },
          },
        ],
      }),
    [testHorizon],
  );

  const yearRows = useMemo(() => {
    const models = ['naive', 'lightgbm_direct'] as const;
    return models.flatMap((model) =>
      [2022, 2023].map((year) => {
        const subset = metrics.by_year.filter(
          (row) => row.split === 'test' && row.model === model && row.target_year === year,
        );
        const n = subset.reduce((total, row) => total + row.n, 0);
        const meanRmse =
          n > 0 ? subset.reduce((total, row) => total + row.RMSE * row.n, 0) / n : null;
        return { model, year, n, meanRmse };
      }),
    );
  }, [metrics.by_year]);

  const yearOption = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 38, bottom: 36 },
        tooltip: tooltipStyle,
        legend: {
          top: 0,
          right: 0,
          textStyle: { color: COLORS.muted, fontSize: 11 },
          data: ['Naive persistence', 'LightGBM direct 7'],
        },
        xAxis: { type: 'category', data: ['2022', '2023'], ...axisStyle },
        yAxis: {
          type: 'value',
          name: 'RMSE (m³/s)',
          nameTextStyle: { color: COLORS.muted, fontSize: 11 },
          ...axisStyle,
        },
        series: [
          {
            name: 'Naive persistence',
            type: 'bar',
            data: ['2022', '2023'].map(
              (year) => yearRows.find((row) => row.model === 'naive' && row.year === Number(year))?.meanRmse ?? null,
            ),
            itemStyle: { color: 'rgba(91, 107, 124, 0.65)', borderRadius: [3, 3, 0, 0] },
            barMaxWidth: 36,
          },
          {
            name: 'LightGBM direct 7',
            type: 'bar',
            data: ['2022', '2023'].map(
              (year) =>
                yearRows.find((row) => row.model === 'lightgbm_direct' && row.year === Number(year))?.meanRmse ?? null,
            ),
            itemStyle: { color: 'rgba(194, 65, 12, 0.8)', borderRadius: [3, 3, 0, 0] },
            barMaxWidth: 36,
          },
        ],
      }),
    [yearRows],
  );

  const overallColumns: Column<MetricOverall>[] = [
    {
      key: 'model',
      label: 'Mô hình',
      render: (row) => (
        <span className={row.model === 'naive' ? 'model-name model-name--best' : 'model-name'}>
          {manifest.model_labels[row.model] ?? row.model}
        </span>
      ),
    },
    {
      key: 'mean_RMSE_7',
      label: 'Mean RMSE 7',
      align: 'right',
      render: (row) => fmtNumber(row.mean_RMSE_7),
    },
    {
      key: 'mean_MAE_7',
      label: 'Mean MAE 7',
      align: 'right',
      render: (row) => fmtNumber(row.mean_MAE_7),
    },
    {
      key: 'mean_NSE_7',
      label: 'Mean NSE 7',
      align: 'right',
      render: (row) => fmtNumber(row.mean_NSE_7, 3),
    },
    {
      key: 'pooled_RMSE',
      label: 'Pooled RMSE',
      align: 'right',
      render: (row) => fmtNumber(row.pooled_RMSE),
    },
    {
      key: 'pooled_NSE',
      label: 'Pooled NSE',
      align: 'right',
      render: (row) => fmtNumber(row.pooled_NSE, 3),
    },
    { key: 'n_pairs', label: 'Số cặp', align: 'right', render: (row) => fmtNumber(row.n_pairs, 0) },
  ];

  const horizonColumns: Column<MetricHorizon>[] = [
    { key: 'horizon', label: 'Horizon', align: 'center', render: (row) => `D+${row.horizon}` },
    {
      key: 'model',
      label: 'Mô hình',
      render: (row) => manifest.model_labels[row.model] ?? row.model,
    },
    { key: 'RMSE', label: 'RMSE', align: 'right', render: (row) => fmtNumber(row.RMSE) },
    { key: 'MAE', label: 'MAE', align: 'right', render: (row) => fmtNumber(row.MAE) },
    { key: 'NSE', label: 'NSE', align: 'right', render: (row) => fmtNumber(row.NSE, 3) },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Q3 · So sánh mô hình</p>
        <h1>Naive và LightGBM gần như hòa nhau</h1>
        <p>
          LightGBM chỉ nhỉnh hơn ở D+1; từ D+2 đến D+7, Naive persistence có RMSE thấp hơn một chút.
          Seasonal Naive 365 kém rõ rệt. Kết quả này được báo cáo nguyên trạng, không tinh chỉnh
          trên Test.
        </p>
      </header>

      <ChartPanel
        kicker="Tổng hợp Test"
        title="Sai số trung bình trên 724 ngày gốc"
        description="Mean RMSE/MAE/NSE lấy trung bình trên 7 horizon; pooled tính trên toàn bộ 5.068 cặp dự báo."
        actions={
          <button className="text-link" type="button" onClick={() => onNavigate('forecast')}>
            Xem một dự báo cụ thể
          </button>
        }
      >
        <DataTable
          columns={overallColumns}
          rows={testOverall}
          rowKey={(row) => row.model}
          caption="So sánh các mô hình trên Test"
        />
      </ChartPanel>

      <div className="two-column">
        <ChartPanel
          kicker="Theo horizon"
          title="RMSE tăng dần khi xa ngày gốc"
          description="Sai số tăng từ D+1 đến D+7 là hành vi hợp lý của dự báo chuỗi thời gian."
        >
          <EChart option={rmseOption} height="330px" ariaLabel="Biểu đồ RMSE theo horizon của Naive và LightGBM" />
        </ChartPanel>
        <ChartPanel
          kicker="Theo horizon"
          title="NSE vẫn trên 0,8 ở D+7"
          description="Cả hai mô hình đều giải thích phần lớn biến thiên ở D+1; mức giải thích giảm dần khi horizon tăng."
        >
          <EChart option={nseOption} height="330px" ariaLabel="Biểu đồ NSE theo horizon của Naive và LightGBM" />
        </ChartPanel>
      </div>

      <ChartPanel
        kicker="Theo năm mục tiêu"
        title="RMSE trung bình theo năm"
        description="Trung bình có trọng số theo số cặp của 7 horizon. Năm 2023 khó hơn 2022 với cả hai mô hình."
      >
        <EChart option={yearOption} height="300px" ariaLabel="Biểu đồ RMSE trung bình theo năm 2022 và 2023" />
      </ChartPanel>

      <ChartPanel
        kicker="Bảng chi tiết"
        title="RMSE, MAE, NSE từng horizon"
        description="Chỉ hiển thị Naive persistence và LightGBM direct 7; Seasonal Naive 365 giữ trong bảng tổng hợp."
      >
        <DataTable
          columns={horizonColumns}
          rows={testHorizon}
          rowKey={(row) => `${row.model}-${row.horizon}`}
          caption="Sai số theo từng horizon trên Test"
        />
      </ChartPanel>

      <aside className="callout callout--warning">
        <strong>Đừng chọn mô hình bằng Test.</strong> Mô hình và siêu tham số được chọn trên
        Validation; Test chỉ dùng một lần để báo cáo. Việc Naive nhỉnh hơn LightGBM cho thấy chuỗi
        rất gần random-walk ở tần suất ngày, và mô hình học máy chưa tạo được lợi thế ổn định.
      </aside>
    </div>
  );
}
