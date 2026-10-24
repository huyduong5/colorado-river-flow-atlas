import type {
  DailyObservation,
  ExtremeEvent,
  ExtremesPayload,
  ForecastIllustrative,
  ForecastRow,
  HeatmapData,
  Manifest,
  MetricHorizon,
  MetricOverall,
  MetricYear,
  MetricsPayload,
  MonthlyStat,
  PredictionsPayload,
  Q1Summary,
  Q2Summary,
  SeasonalityPayload,
  SeasonalitySummary,
  YearlyStat,
} from '../types';

const base = import.meta.env.BASE_URL;

function invalid(file: string, message: string): never {
  throw new Error(`Dữ liệu ${file} không hợp lệ: ${message}`);
}

function asRecord(value: unknown, file: string, field: string): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    invalid(file, `${field} phải là object`);
  }
  return value as Record<string, unknown>;
}

function asArray(value: unknown, file: string, field: string): unknown[] {
  if (!Array.isArray(value)) invalid(file, `${field} phải là mảng`);
  return value;
}

function asString(value: unknown, file: string, field: string): string {
  if (typeof value !== 'string' || value.length === 0) invalid(file, `${field} phải là chuỗi`);
  return value;
}

function asNumber(value: unknown, file: string, field: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    invalid(file, `${field} phải là số hữu hạn`);
  }
  return value;
}

function asNullableNumber(value: unknown, file: string, field: string): number | null {
  if (value === null) return null;
  return asNumber(value, file, field);
}

function asStringArray(value: unknown, file: string, field: string): string[] {
  return asArray(value, file, field).map((item, index) =>
    asString(item, file, `${field}[${index}]`),
  );
}

function asNumberArray(value: unknown, file: string, field: string): number[] {
  return asArray(value, file, field).map((item, index) =>
    asNumber(item, file, `${field}[${index}]`),
  );
}

function validateManifest(value: unknown, file: string): Manifest {
  const root = asRecord(value, file, 'root');
  const scopes = asRecord(root.date_scopes, file, 'date_scopes');
  const observations = asRecord(scopes.observations, file, 'date_scopes.observations');
  const test = asRecord(scopes.test, file, 'date_scopes.test');
  const definitions = asRecord(root.definitions, file, 'definitions');
  const labels = asRecord(root.model_labels, file, 'model_labels');
  return {
    schema_version: asString(root.schema_version, file, 'schema_version'),
    run_id: asString(root.run_id, file, 'run_id'),
    dataset_hash: asString(root.dataset_hash, file, 'dataset_hash'),
    created_at_utc: asString(root.created_at_utc, file, 'created_at_utc'),
    models: asStringArray(root.models, file, 'models'),
    model_labels: Object.fromEntries(
      Object.entries(labels).map(([key, value]) => [key, asString(value, file, `model_labels.${key}`)]),
    ),
    date_scopes: {
      observations: {
        start: asString(observations.start, file, 'date_scopes.observations.start'),
        end: asString(observations.end, file, 'date_scopes.observations.end'),
      },
      test: {
        start: asString(test.start, file, 'date_scopes.test.start'),
        end: asString(test.end, file, 'date_scopes.test.end'),
      },
    },
    definitions: {
      threshold_scope: asString(definitions.threshold_scope, file, 'definitions.threshold_scope'),
      threshold_quantile: asNumber(
        definitions.threshold_quantile,
        file,
        'definitions.threshold_quantile',
      ),
      horizon_days: asNumber(definitions.horizon_days, file, 'definitions.horizon_days'),
      metrics: asStringArray(definitions.metrics, file, 'definitions.metrics'),
    },
    files: asStringArray(root.files, file, 'files'),
  };
}

function validateDaily(value: unknown, file: string): DailyObservation[] {
  return asArray(value, file, 'root').map((item, index) => {
    const row = asRecord(item, file, `[${index}]`);
    return {
      date: asString(row.date, file, `[${index}].date`),
      q: asNumber(row.q, file, `[${index}].q`),
    };
  });
}

function validateMonthly(value: unknown, file: string): MonthlyStat[] {
  return asArray(value, file, 'root').map((item, index) => {
    const row = asRecord(item, file, `[${index}]`);
    return {
      month: asNumber(row.month, file, `[${index}].month`),
      n: asNumber(row.n, file, `[${index}].n`),
      mean: asNumber(row.mean, file, `[${index}].mean`),
      median: asNumber(row.median, file, `[${index}].median`),
      std_sample: asNumber(row.std_sample, file, `[${index}].std_sample`),
      min: asNumber(row.min, file, `[${index}].min`),
      p25: asNumber(row.p25, file, `[${index}].p25`),
      p75: asNumber(row.p75, file, `[${index}].p75`),
      max: asNumber(row.max, file, `[${index}].max`),
    };
  });
}

function validateYearly(value: unknown, file: string): YearlyStat[] {
  return asArray(value, file, 'root').map((item, index) => {
    const row = asRecord(item, file, `[${index}]`);
    return {
      year: asNumber(row.year, file, `[${index}].year`),
      n: asNumber(row.n, file, `[${index}].n`),
      mean: asNumber(row.mean, file, `[${index}].mean`),
      median: asNumber(row.median, file, `[${index}].median`),
      std_sample: asNumber(row.std_sample, file, `[${index}].std_sample`),
      min: asNumber(row.min, file, `[${index}].min`),
      p95: asNumber(row.p95, file, `[${index}].p95`),
      max: asNumber(row.max, file, `[${index}].max`),
    };
  });
}

function validateHeatmap(value: unknown, file: string): HeatmapData {
  const root = asRecord(value, file, 'root');
  const years = asNumberArray(root.years, file, 'years');
  const values = asArray(root.values, file, 'values').map((row, index) =>
    asNumberArray(row, file, `values[${index}]`),
  );
  if (values.length !== years.length || values.some((row) => row.length !== 12)) {
    invalid(file, 'values phải có 12 tháng cho mỗi năm');
  }
  return { years, values };
}

function validateExtremeEvent(value: unknown, file: string, field: string): ExtremeEvent {
  const row = asRecord(value, file, field);
  return {
    event_id: asString(row.event_id, file, `${field}.event_id`),
    start_date: asString(row.start_date, file, `${field}.start_date`),
    end_date: asString(row.end_date, file, `${field}.end_date`),
    duration_days: asNumber(row.duration_days, file, `${field}.duration_days`),
    peak_date: asString(row.peak_date, file, `${field}.peak_date`),
    peak_flow: asNumber(row.peak_flow, file, `${field}.peak_flow`),
    n_exceedance_days: asNumber(
      row.n_exceedance_days,
      file,
      `${field}.n_exceedance_days`,
    ),
    threshold_value: asNumber(row.threshold_value, file, `${field}.threshold_value`),
    threshold_scope: asString(row.threshold_scope, file, `${field}.threshold_scope`),
    rank: row.rank === undefined ? undefined : asNumber(row.rank, file, `${field}.rank`),
  };
}

function validateExtremes(value: unknown, file: string): ExtremesPayload {
  const root = asRecord(value, file, 'root');
  const summary = asRecord(root.summary, file, 'summary');
  const events = asArray(root.events, file, 'events').map((item, index) =>
    validateExtremeEvent(item, file, `events[${index}]`),
  );
  const top5 = asArray(root.top5, file, 'top5').map((item, index) =>
    validateExtremeEvent(item, file, `top5[${index}]`),
  );
  const q2: Q2Summary = {
    threshold: asNumber(summary.threshold, file, 'summary.threshold'),
    quantile: asNumber(summary.quantile, file, 'summary.quantile'),
    mean: asNumber(summary.mean, file, 'summary.mean'),
    std_sample: asNumber(summary.std_sample, file, 'summary.std_sample'),
    z_threshold: asNumber(summary.z_threshold, file, 'summary.z_threshold'),
    n_days_high: asNumber(summary.n_days_high, file, 'summary.n_days_high'),
    share_days_high: asNumber(summary.share_days_high, file, 'summary.share_days_high'),
    n_events: asNumber(summary.n_events, file, 'summary.n_events'),
    longest_event_days: asNumber(summary.longest_event_days, file, 'summary.longest_event_days'),
    max_event_peak: asNumber(summary.max_event_peak, file, 'summary.max_event_peak'),
    peak_year: asNumber(summary.peak_year, file, 'summary.peak_year'),
  };
  return { summary: q2, events, top5 };
}

function validateMetricOverall(value: unknown, file: string, field: string): MetricOverall {
  const row = asRecord(value, file, field);
  return {
    run_id: asString(row.run_id, file, `${field}.run_id`),
    model: asString(row.model, file, `${field}.model`),
    split: asString(row.split, file, `${field}.split`),
    n_origins: asNumber(row.n_origins, file, `${field}.n_origins`),
    n_pairs: asNumber(row.n_pairs, file, `${field}.n_pairs`),
    mean_RMSE_7: asNumber(row.mean_RMSE_7, file, `${field}.mean_RMSE_7`),
    mean_MAE_7: asNumber(row.mean_MAE_7, file, `${field}.mean_MAE_7`),
    mean_NSE_7: asNumber(row.mean_NSE_7, file, `${field}.mean_NSE_7`),
    pooled_RMSE: asNumber(row.pooled_RMSE, file, `${field}.pooled_RMSE`),
    pooled_MAE: asNumber(row.pooled_MAE, file, `${field}.pooled_MAE`),
    pooled_NSE: asNumber(row.pooled_NSE, file, `${field}.pooled_NSE`),
  };
}

function validateMetricHorizon(value: unknown, file: string, field: string): MetricHorizon {
  const row = asRecord(value, file, field);
  return {
    run_id: asString(row.run_id, file, `${field}.run_id`),
    model: asString(row.model, file, `${field}.model`),
    split: asString(row.split, file, `${field}.split`),
    horizon: asNumber(row.horizon, file, `${field}.horizon`),
    n: asNumber(row.n, file, `${field}.n`),
    RMSE: asNumber(row.RMSE, file, `${field}.RMSE`),
    MAE: asNumber(row.MAE, file, `${field}.MAE`),
    NSE: asNumber(row.NSE, file, `${field}.NSE`),
  };
}

function validateMetricYear(value: unknown, file: string, field: string): MetricYear {
  const row = asRecord(value, file, field);
  return {
    run_id: asString(row.run_id, file, `${field}.run_id`),
    model: asString(row.model, file, `${field}.model`),
    split: asString(row.split, file, `${field}.split`),
    target_year: asNumber(row.target_year, file, `${field}.target_year`),
    horizon: asNumber(row.horizon, file, `${field}.horizon`),
    n: asNumber(row.n, file, `${field}.n`),
    RMSE: asNumber(row.RMSE, file, `${field}.RMSE`),
    MAE: asNumber(row.MAE, file, `${field}.MAE`),
    NSE: asNumber(row.NSE, file, `${field}.NSE`),
  };
}

function validateMetrics(value: unknown, file: string): MetricsPayload {
  const root = asRecord(value, file, 'root');
  return {
    overall: asArray(root.overall, file, 'overall').map((item, index) =>
      validateMetricOverall(item, file, `overall[${index}]`),
    ),
    by_horizon: asArray(root.by_horizon, file, 'by_horizon').map((item, index) =>
      validateMetricHorizon(item, file, `by_horizon[${index}]`),
    ),
    by_year: asArray(root.by_year, file, 'by_year').map((item, index) =>
      validateMetricYear(item, file, `by_year[${index}]`),
    ),
  };
}

function validateQ1(value: unknown, file: string): Q1Summary {
  const q1 = asRecord(value, file, 'q1');
  const minMonth = asRecord(q1.monthly_mean_min, file, 'q1.monthly_mean_min');
  const maxMonth = asRecord(q1.monthly_mean_max, file, 'q1.monthly_mean_max');
  const minYear = asRecord(q1.yearly_mean_min, file, 'q1.yearly_mean_min');
  const maxYear = asRecord(q1.yearly_mean_max, file, 'q1.yearly_mean_max');
  return {
    monthly_mean_min: {
      month: asNumber(minMonth.month, file, 'q1.monthly_mean_min.month'),
      value: asNumber(minMonth.value, file, 'q1.monthly_mean_min.value'),
    },
    monthly_mean_max: {
      month: asNumber(maxMonth.month, file, 'q1.monthly_mean_max.month'),
      value: asNumber(maxMonth.value, file, 'q1.monthly_mean_max.value'),
    },
    yearly_mean_min: {
      year: asNumber(minYear.year, file, 'q1.yearly_mean_min.year'),
      value: asNumber(minYear.value, file, 'q1.yearly_mean_min.value'),
    },
    yearly_mean_max: {
      year: asNumber(maxYear.year, file, 'q1.yearly_mean_max.year'),
      value: asNumber(maxYear.value, file, 'q1.yearly_mean_max.value'),
    },
    monthly_amplitude_mean: asNumber(
      q1.monthly_amplitude_mean,
      file,
      'q1.monthly_amplitude_mean',
    ),
    yearly_amplitude_mean: asNumber(
      q1.yearly_amplitude_mean,
      file,
      'q1.yearly_amplitude_mean',
    ),
  };
}

function validateSeasonality(value: unknown, file: string): SeasonalityPayload {
  const root = asRecord(value, file, 'root');
  const summary = asRecord(root.summary, file, 'summary');
  const seasonality: SeasonalitySummary = {
    stl_period_days: asNumber(summary.stl_period_days, file, 'summary.stl_period_days'),
    stl_robust: summary.stl_robust === true,
    seasonal_strength: asNumber(summary.seasonal_strength, file, 'summary.seasonal_strength'),
    trend_strength: asNumber(summary.trend_strength, file, 'summary.trend_strength'),
    acf_lag_365: asNumber(summary.acf_lag_365, file, 'summary.acf_lag_365'),
    acf_lag_182: asNumber(summary.acf_lag_182, file, 'summary.acf_lag_182'),
    acf_lag_30: asNumber(summary.acf_lag_30, file, 'summary.acf_lag_30'),
    acf_lag_7: asNumber(summary.acf_lag_7, file, 'summary.acf_lag_7'),
    trend_start: asNumber(summary.trend_start, file, 'summary.trend_start'),
    trend_end: asNumber(summary.trend_end, file, 'summary.trend_end'),
    trend_min: asNumber(summary.trend_min, file, 'summary.trend_min'),
    trend_max: asNumber(summary.trend_max, file, 'summary.trend_max'),
  };
  return { summary: seasonality, q1: validateQ1(root.q1, file) };
}

function validateForecastRow(value: unknown, file: string, field: string): ForecastRow {
  const row = asRecord(value, file, field);
  return {
    run_id: asString(row.run_id, file, `${field}.run_id`),
    model: asString(row.model, file, `${field}.model`),
    origin_date: asString(row.origin_date, file, `${field}.origin_date`),
    target_date: asString(row.target_date, file, `${field}.target_date`),
    horizon: asNumber(row.horizon, file, `${field}.horizon`),
    y_true: asNullableNumber(row.y_true, file, `${field}.y_true`),
    y_pred: asNumber(row.y_pred, file, `${field}.y_pred`),
    split: asString(row.split, file, `${field}.split`),
  };
}

function validatePredictions(value: unknown, file: string): PredictionsPayload {
  const root = asRecord(value, file, 'root');
  const labels = asRecord(root.labels, file, 'labels');
  return {
    models: asStringArray(root.models, file, 'models'),
    labels: Object.fromEntries(
      Object.entries(labels).map(([key, value]) => [key, asString(value, file, `labels.${key}`)]),
    ),
    rows: asArray(root.rows, file, 'rows').map((item, index) =>
      validateForecastRow(item, file, `rows[${index}]`),
    ),
  };
}

function validateIllustrative(value: unknown, file: string): ForecastIllustrative[] {
  return asArray(value, file, 'root').map((item, index) => {
    const row = asRecord(item, file, `[${index}]`);
    return {
      model: asString(row.model, file, `[${index}].model`),
      origin_date: asString(row.origin_date, file, `[${index}].origin_date`),
      target_date: asString(row.target_date, file, `[${index}].target_date`),
      horizon: asNumber(row.horizon, file, `[${index}].horizon`),
      y_true: asNullableNumber(row.y_true, file, `[${index}].y_true`),
      y_pred: asNumber(row.y_pred, file, `[${index}].y_pred`),
    };
  });
}

async function loadJson<T>(
  name: string,
  validate: (value: unknown, file: string) => T,
): Promise<T> {
  const response = await fetch(`${base}data/${name}`);
  if (!response.ok) {
    throw new Error(`Không tải được ${name} (${response.status})`);
  }
  return validate(await response.json(), name);
}

export const loadManifest = () => loadJson('manifest.json', validateManifest);
export const loadDaily = () => loadJson('daily.json', validateDaily);
export const loadMonthly = () => loadJson('monthly.json', validateMonthly);
export const loadYearly = () => loadJson('yearly.json', validateYearly);
export const loadHeatmap = () => loadJson('heatmap.json', validateHeatmap);
export const loadExtremes = () => loadJson('extremes.json', validateExtremes);
export const loadMetrics = () => loadJson('metrics.json', validateMetrics);
export const loadSeasonality = () => loadJson('seasonality.json', validateSeasonality);
export const loadPredictions = () => loadJson('predictions.json', validatePredictions);
export const loadIllustrative = () => loadJson('forecast_illustrative.json', validateIllustrative);
