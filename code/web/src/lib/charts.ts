import type { EChartsOption } from 'echarts';

export const COLORS = {
  ink: '#0b1f33',
  muted: '#5b6b7c',
  blue: '#155e9e',
  cyan: '#0e7490',
  orange: '#c2410c',
  red: '#b91c1c',
  green: '#15803d',
  grid: '#dbe4ee',
  paper: '#ffffff',
  navy: '#0b1f33',
};

export const FONT_FAMILY =
  '"Segoe UI", "Helvetica Neue", Helvetica, Arial, "Noto Sans", sans-serif';

export const axisStyle = {
  axisLine: { lineStyle: { color: '#b8c6d6' } },
  axisTick: { lineStyle: { color: '#b8c6d6' } },
  axisLabel: { color: COLORS.muted, fontSize: 11, fontFamily: FONT_FAMILY },
  splitLine: { lineStyle: { color: COLORS.grid, type: 'dashed' as const } },
};

export const tooltipStyle = {
  trigger: 'axis' as const,
  backgroundColor: COLORS.ink,
  borderWidth: 0,
  padding: [8, 12],
  textStyle: { color: '#f8fafc', fontSize: 12, fontFamily: FONT_FAMILY },
  axisPointer: { lineStyle: { color: '#94a3b8' } },
};

export const gridStyle = { left: 52, right: 24, top: 36, bottom: 44 };

export function flowLabel(value: number): string {
  return `${new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 1 }).format(value)} m³/s`;
}

export function baseOption(overrides?: EChartsOption): EChartsOption {
  return {
    textStyle: { fontFamily: FONT_FAMILY, color: COLORS.ink },
    aria: { enabled: true },
    animationDuration: 450,
    toolbox: {
      left: 'center',
      top: 0,
      itemSize: 15,
      itemGap: 10,
      iconStyle: { borderColor: COLORS.muted, color: COLORS.muted },
      feature: {
        dataZoom: { title: { zoom: 'Thu phóng vùng', back: 'Hoàn tác thu phóng' } },
        restore: { title: 'Khôi phục' },
        saveAsImage: {
          title: 'Tải PNG',
          name: 'colorado-river-flow',
          pixelRatio: 2,
          backgroundColor: '#ffffff',
        },
      },
    },
    ...overrides,
  };
}
