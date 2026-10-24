import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const dataDir = join(root, 'public', 'data');
const downloadsDir = join(root, 'public', 'downloads');
const read = (name) => JSON.parse(readFileSync(join(dataDir, name), 'utf8'));

const manifest = read('manifest.json');
const daily = read('daily.json');
const extremes = read('extremes.json');
const metrics = read('metrics.json');
const predictions = read('predictions.json');
const heatmap = read('heatmap.json');

assert.equal(manifest.schema_version, '1.0');
assert.equal(manifest.dataset_hash, 'f83d984747fe12e5e31aa71e794e71d40f30c6dc6711544cb54ec5e7a9f83660');
assert.equal(manifest.definitions.horizon_days, 7);
assert.equal(manifest.definitions.threshold_quantile, 0.95);
assert.equal(daily.length, 5113);
assert.equal(daily[0].date, '2010-01-01');
assert.equal(daily.at(-1).date, '2023-12-31');
assert.equal(extremes.summary.n_events, 15);
assert.equal(extremes.summary.n_days_high, 256);
assert.equal(extremes.summary.threshold.toFixed(6), '417.230854');
assert.equal(heatmap.years.length, 14);
assert.equal(heatmap.values.length, 14);
assert.ok(heatmap.values.every((row) => row.length === 12));

const test = metrics.overall.filter((row) => row.split === 'test');
assert.equal(test.length, 3);
assert.ok(test.every((row) => row.run_id === manifest.run_id));
assert.ok(metrics.by_horizon.every((row) => row.run_id === manifest.run_id));
assert.equal(metrics.by_horizon.filter((row) => row.split === 'test').length, 21);
const naive = test.find((row) => row.model === 'naive');
const lgbm = test.find((row) => row.model === 'lightgbm_direct');
assert.ok(naive && lgbm);
assert.equal(naive.n_pairs, 5068);
assert.equal(lgbm.n_pairs, 5068);
assert.ok(naive.mean_RMSE_7 < lgbm.mean_RMSE_7);

assert.equal(predictions.rows.length, 15204);
assert.equal(new Set(predictions.rows.map((row) => row.model)).size, 3);
assert.ok(predictions.rows.every((row) => Number.isFinite(row.y_pred)));
const origins = new Set(predictions.rows.map((row) => row.origin_date.slice(0, 10)));
assert.equal(origins.size, 724);
for (const origin of origins) {
  const rows = predictions.rows.filter((row) => row.origin_date.slice(0, 10) === origin);
  assert.equal(rows.length, 21);
}

for (const name of [
  'predictions_long.csv',
  'metrics_overall.csv',
  'metrics_by_horizon.csv',
  'extreme_events.csv',
  'colorado_river_flow_processed.csv',
  'bao_cao.pdf',
  'latex_overleaf.zip',
  'source_code.zip',
]) {
  const path = join(downloadsDir, name);
  assert.ok(existsSync(path), `Thiếu ${name}`);
  assert.ok(readFileSync(path).length > 100, `${name} rỗng hoặc quá nhỏ`);
}

console.log('Web smoke tests passed: 5.113 ngày, 15 đợt, 5.068 cặp dự báo.');
