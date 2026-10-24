export interface Manifest {
  schema_version: string;
  run_id: string;
  dataset_hash: string;
  created_at_utc: string;
  models: string[];
  model_labels: Record<string, string>;
  date_scopes: {
    observations: { start: string; end: string };
    test: { start: string; end: string };
  };
  definitions: {
    threshold_scope: string;
    threshold_quantile: number;
    horizon_days: number;
    metrics: string[];
  };
  files: string[];
}

export interface DailyObservation {
  date: string;
  q: number;
}

export interface MonthlyStat {
  month: number;
  n: number;
  mean: number;
  median: number;
  std_sample: number;
  min: number;
  p25: number;
  p75: number;
  max: number;
}

export interface YearlyStat {
  year: number;
  n: number;
  mean: number;
  median: number;
  std_sample: number;
  min: number;
  p95: number;
  max: number;
}

export interface HeatmapData {
  years: number[];
  values: number[][];
}

export interface ExtremeEvent {
  event_id: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  peak_date: string;
  peak_flow: number;
  n_exceedance_days: number;
  threshold_value: number;
  threshold_scope: string;
  rank?: number;
}

export interface Q2Summary {
  threshold: number;
  quantile: number;
  mean: number;
  std_sample: number;
  z_threshold: number;
  n_days_high: number;
  share_days_high: number;
  n_events: number;
  longest_event_days: number;
  max_event_peak: number;
  peak_year: number;
}

export interface ExtremesPayload {
  summary: Q2Summary;
  events: ExtremeEvent[];
  top5: ExtremeEvent[];
}

export interface MetricOverall {
  run_id: string;
  model: string;
  split: string;
  n_origins: number;
  n_pairs: number;
  mean_RMSE_7: number;
  mean_MAE_7: number;
  mean_NSE_7: number;
  pooled_RMSE: number;
  pooled_MAE: number;
  pooled_NSE: number;
}

export interface MetricHorizon {
  run_id: string;
  model: string;
  split: string;
  horizon: number;
  n: number;
  RMSE: number;
  MAE: number;
  NSE: number;
}

export interface MetricYear {
  run_id: string;
  model: string;
  split: string;
  target_year: number;
  horizon: number;
  n: number;
  RMSE: number;
  MAE: number;
  NSE: number;
}

export interface MetricsPayload {
  overall: MetricOverall[];
  by_horizon: MetricHorizon[];
  by_year: MetricYear[];
}

export interface ForecastRow {
  run_id: string;
  model: string;
  origin_date: string;
  target_date: string;
  horizon: number;
  y_true: number | null;
  y_pred: number;
  split: string;
}

export interface PredictionsPayload {
  models: string[];
  labels: Record<string, string>;
  rows: ForecastRow[];
}

export interface Q1Summary {
  monthly_mean_min: { month: number; value: number };
  monthly_mean_max: { month: number; value: number };
  yearly_mean_min: { year: number; value: number };
  yearly_mean_max: { year: number; value: number };
  monthly_amplitude_mean: number;
  yearly_amplitude_mean: number;
}

export interface SeasonalitySummary {
  stl_period_days: number;
  stl_robust: boolean;
  seasonal_strength: number;
  trend_strength: number;
  acf_lag_365: number;
  acf_lag_182: number;
  acf_lag_30: number;
  acf_lag_7: number;
  trend_start: number;
  trend_end: number;
  trend_min: number;
  trend_max: number;
}

export interface SeasonalityPayload {
  summary: SeasonalitySummary;
  q1: Q1Summary;
}

export interface ForecastIllustrative {
  model: string;
  origin_date: string;
  target_date: string;
  horizon: number;
  y_true: number | null;
  y_pred: number;
}

export type PageId =
  | 'overview'
  | 'explore'
  | 'seasonality'
  | 'extremes'
  | 'forecast'
  | 'models'
  | 'methods'
  | 'downloads';
