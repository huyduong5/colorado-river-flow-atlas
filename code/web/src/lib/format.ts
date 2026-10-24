const nf = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 });
const nf3 = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 3 });

export function fmtNumber(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return 'NA';
  return digits >= 3 ? nf3.format(value) : nf.format(value);
}

export function fmtPercent(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return 'NA';
  return `${fmtNumber(value * 100, digits)}%`;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return 'NA';
  const [y, m, d] = iso.slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}

export function fmtMonth(month: number): string {
  return `T${month}`;
}

export function fmtYearMonth(year: number, month: number): string {
  return `${String(month).padStart(2, '0')}/${year}`;
}

export function downloadCsv(filename: string, rows: string[][]): void {
  const csv = rows.map((row) => row.map((cell) => `"${cell.replaceAll('"', '""')}"`).join(',')).join('\n');
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
