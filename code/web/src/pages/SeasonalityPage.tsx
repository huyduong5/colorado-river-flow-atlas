import { useMemo } from 'react';
import type { HeatmapData, MonthlyStat, SeasonalityPayload, YearlyStat } from '../types';
import { ChartPanel } from '../components/ChartPanel';
import { EChart } from '../components/EChart';
import { axisStyle, baseOption, COLORS, gridStyle, tooltipStyle } from '../lib/charts';
import { fmtMonth, fmtNumber } from '../lib/format';

interface SeasonalityPageProps {
  monthly: MonthlyStat[];
  yearly: YearlyStat[];
  heatmap: HeatmapData;
  seasonality: SeasonalityPayload;
}

export function SeasonalityPage({ monthly, yearly, heatmap, seasonality }: SeasonalityPageProps) {
  const months = monthly.map((row) => fmtMonth(row.month));
  const boxData = monthly.map((row) => [row.min, row.p25, row.median, row.p75, row.max]);
  const means = monthly.map((row) => row.mean);
  const overallMean = useMemo(() => {
    const n = yearly.reduce((total, row) => total + row.n, 0);
    return n > 0 ? yearly.reduce((total, row) => total + row.mean * row.n, 0) / n : 0;
  }, [yearly]);
  const heatmapRange = useMemo(() => {
    const values = heatmap.values.flat();
    return {
      min: Math.floor(Math.min(...values) / 20) * 20,
      max: Math.ceil(Math.max(...values) / 20) * 20,
    };
  }, [heatmap]);

  const boxOption = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 34, bottom: 38 },
        tooltip: { ...tooltipStyle, trigger: 'item' },
        legend: {
          top: 0,
          right: 0,
          textStyle: { color: COLORS.muted, fontSize: 11 },
          data: ['Phân bố tháng', 'Trung bình tháng'],
        },
        xAxis: { type: 'category', data: months, ...axisStyle },
        yAxis: {
          type: 'value',
          name: 'm³/s',
          nameTextStyle: { color: COLORS.muted, fontSize: 11 },
          ...axisStyle,
        },
        series: [
          {
            name: 'Phân bố tháng',
            type: 'boxplot',
            data: boxData,
            itemStyle: { color: 'rgba(21, 94, 158, 0.12)', borderColor: COLORS.blue },
            boxWidth: ['18%', '42%'],
          },
          {
            name: 'Trung bình tháng',
            type: 'line',
            data: means,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { color: COLORS.orange, width: 2 },
            itemStyle: { color: COLORS.orange },
          },
        ],
      }),
    [boxData, means, months],
  );

  const yearlyOption = useMemo(
    () =>
      baseOption({
        grid: { ...gridStyle, top: 24, bottom: 40 },
        tooltip: tooltipStyle,
        xAxis: { type: 'category', data: yearly.map((row) => String(row.year)), ...axisStyle },
        yAxis: {
          type: 'value',
          name: 'm³/s',
          nameTextStyle: { color: COLORS.muted, fontSize: 11 },
          ...axisStyle,
        },
        series: [
          {
            name: 'Trung bình năm',
            type: 'bar',
            data: yearly.map((row) => row.mean),
            barMaxWidth: 28,
            itemStyle: { color: COLORS.blue, borderRadius: [3, 3, 0, 0] },
          },
          {
            name: 'Trung bình toàn chuỗi',
            type: 'line',
            data: yearly.map(() => overallMean),
            symbol: 'none',
            lineStyle: { color: COLORS.muted, type: 'dashed', width: 1 },
          },
        ],
      }),
    [overallMean, yearly],
  );

  const heatOption = useMemo(() => {
    const data: [number, number, number][] = [];
    heatmap.years.forEach((year, yearIndex) => {
      heatmap.values[yearIndex]?.forEach((value, monthIndex) => {
        data.push([monthIndex, yearIndex, value]);
      });
    });
    return baseOption({
      grid: { left: 48, right: 18, top: 16, bottom: 58 },
      tooltip: { ...tooltipStyle, trigger: 'item' },
      xAxis: { type: 'category', data: months, ...axisStyle, splitArea: { show: true } },
      yAxis: { type: 'category', data: heatmap.years.map(String), ...axisStyle, splitArea: { show: true } },
      visualMap: {
        min: heatmapRange.min,
        max: heatmapRange.max,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        itemWidth: 14,
        itemHeight: 160,
        textGap: 8,
        textStyle: { color: COLORS.muted, fontSize: 10 },
        inRange: { color: ['#eaf2f8', '#9cc3dd', '#4b8fbd', '#155e9e', '#c2410c'] },
      },
      series: [
        {
          name: 'Trung bình tháng theo năm',
          type: 'heatmap',
          data,
          label: { show: false },
          itemStyle: { borderColor: '#ffffff', borderWidth: 1 },
          emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(11,31,51,0.35)' } },
        },
      ],
    });
  }, [heatmap, heatmapRange, months]);

  return (
    <div className="page">
      <header className="page-header">
        <p className="kicker">Q1 · Xu hướng & mùa vụ</p>
        <h1>Mùa vụ yếu hơn biến thiên giữa các năm</h1>
        <p>
          Trung bình tháng gần như phẳng, trong khi trung bình năm dao động rất mạnh. Vì vậy không
          nên đọc chuỗi này như một mùa vụ đều đặn kiểu thủy văn ôn đới; cần tách xu hướng và bối
          cảnh từng năm.
        </p>
      </header>

      <section className="stat-grid stat-grid--compact">
        <article className="mini-stat">
          <span>Biên độ trung bình tháng</span>
          <strong>{fmtNumber(seasonality.q1.monthly_amplitude_mean)} m³/s</strong>
        </article>
        <article className="mini-stat">
          <span>Biên độ trung bình năm</span>
          <strong>{fmtNumber(seasonality.q1.yearly_amplitude_mean)} m³/s</strong>
        </article>
        <article className="mini-stat">
          <span>Seasonal strength</span>
          <strong>{fmtNumber(seasonality.summary.seasonal_strength, 3)}</strong>
        </article>
        <article className="mini-stat">
          <span>Trend strength</span>
          <strong>{fmtNumber(seasonality.summary.trend_strength, 3)}</strong>
        </article>
      </section>

      <ChartPanel
        kicker="Phân bố theo tháng"
        title="Boxplot lưu lượng từng tháng"
        description="Hộp cho thấy trung vị và khoảng tứ phân vị; râu kéo đến min/max. Đường cam là trung bình tháng. Các tháng có phân bố rộng do ảnh hưởng của những năm lưu lượng cao."
      >
        <EChart option={boxOption} height="390px" ariaLabel="Boxplot lưu lượng theo từng tháng" />
      </ChartPanel>

      <div className="two-column">
        <ChartPanel
          kicker="Theo năm"
          title="Trung bình năm"
          description="Năm 2010 thấp nhất, năm 2017 cao nhất trong giai đoạn quan sát."
        >
          <EChart option={yearlyOption} height="330px" ariaLabel="Biểu đồ trung bình lưu lượng theo năm" />
        </ChartPanel>
        <ChartPanel
          kicker="STL & tự tương quan"
          title="Tín hiệu mùa vụ"
          description="STL dùng chu kỳ 365 ngày, robust. Seasonal strength thấp; trend strength cao."
        >
          <dl className="definition-list">
            <div>
              <dt>ACF lag 7 ngày</dt>
              <dd>{fmtNumber(seasonality.summary.acf_lag_7, 3)}</dd>
            </div>
            <div>
              <dt>ACF lag 30 ngày</dt>
              <dd>{fmtNumber(seasonality.summary.acf_lag_30, 3)}</dd>
            </div>
            <div>
              <dt>ACF lag 182 ngày</dt>
              <dd>{fmtNumber(seasonality.summary.acf_lag_182, 3)}</dd>
            </div>
            <div>
              <dt>ACF lag 365 ngày</dt>
              <dd>{fmtNumber(seasonality.summary.acf_lag_365, 3)}</dd>
            </div>
            <div>
              <dt>Trend đầu chuỗi</dt>
              <dd>{fmtNumber(seasonality.summary.trend_start)} m³/s</dd>
            </div>
            <div>
              <dt>Trend cuối chuỗi</dt>
              <dd>{fmtNumber(seasonality.summary.trend_end)} m³/s</dd>
            </div>
          </dl>
        </ChartPanel>
      </div>

      <ChartPanel
        kicker="Heatmap"
        title="Trung bình tháng theo từng năm"
        description={`Màu đậm hơn là lưu lượng cao hơn (${heatmapRange.min}–${heatmapRange.max} m³/s). Có thể thấy các năm 2017–2019 nổi bật, không phải một chu kỳ tháng lặp lại ổn định.`}
      >
        <EChart option={heatOption} height="430px" ariaLabel="Heatmap trung bình lưu lượng theo tháng và năm" />
      </ChartPanel>

      <aside className="callout">
        <strong>Kết luận Q1.</strong> Tháng 9 có trung bình thấp nhất ({fmtNumber(seasonality.q1.monthly_mean_min.value)} m³/s),
        tháng 11 cao nhất ({fmtNumber(seasonality.q1.monthly_mean_max.value)} m³/s), nhưng chênh lệch chỉ
        khoảng {fmtNumber(seasonality.q1.monthly_amplitude_mean)} m³/s. Trung bình năm 2010 là{' '}
        {fmtNumber(seasonality.q1.yearly_mean_min.value)} m³/s và năm 2017 là{' '}
        {fmtNumber(seasonality.q1.yearly_mean_max.value)} m³/s. Vì vậy mùa vụ không phải yếu tố chi phối
        chính; biến thiên giữa các năm và các đợt cực trị quan trọng hơn.
      </aside>
    </div>
  );
}
