import { apiFetch } from "./api";

export type PricePoint = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type PriceHistory = {
  ticker: string;
  count: number;
  data: PricePoint[];
};

export type PredictionPoint = { day: number; predicted_close: number };

export type PredictionResponse = {
  ticker: string;
  forecast_days: number;
  cached: boolean;
  predictions: PredictionPoint[];
};

export type TrainQueued = { message: string; ticker: string; task_id: string; status_url: string };

export type TrainStatus = {
  task_id: string;
  state: string; // PENDING | STARTED | RETRY | SUCCESS | FAILURE
  result?: unknown;
  error?: string;
};

export type TrainingRunStatus = "success" | "degraded" | "failed";

export type TrainingRun = {
  id: number;
  ticker: string;
  status: TrainingRunStatus;
  rmse: number | null;
  mae: number | null;
  mape: number | null;
  mse: number | null;
  epochs_run: number | null;
  training_samples: number | null;
  test_samples: number | null;
  notes: string;
  created_at: string;
};

/** GET /stocks/<ticker>/ — yfinance OHLCV history (public). */
export function getPriceHistory(ticker: string, years = 1): Promise<PriceHistory> {
  return apiFetch<PriceHistory>(
    `/stocks/${encodeURIComponent(ticker)}/?years=${years}`,
    { auth: false },
  );
}

/** GET /ml/predict/<ticker>/ — forecast from the trained model (404 if untrained). */
export function getPrediction(ticker: string, days = 30): Promise<PredictionResponse> {
  return apiFetch<PredictionResponse>(
    `/ml/predict/${encodeURIComponent(ticker)}/?days=${days}`,
    { auth: false },
  );
}

/** POST /ml/train/<ticker>/ — queue an async training job. */
export function trainModel(ticker: string, years = 10): Promise<TrainQueued> {
  return apiFetch<TrainQueued>(`/ml/train/${encodeURIComponent(ticker)}/`, {
    method: "POST",
    body: { years },
  });
}

/** GET /ml/train/status/<taskId>/ — poll a training job. */
export function getTrainStatus(taskId: string): Promise<TrainStatus> {
  return apiFetch<TrainStatus>(`/ml/train/status/${encodeURIComponent(taskId)}/`);
}

/** GET /ml/training-runs/<ticker>/ — recent training runs with metrics. */
export function getTrainingRuns(ticker: string, limit = 10): Promise<TrainingRun[]> {
  return apiFetch<TrainingRun[]>(
    `/ml/training-runs/${encodeURIComponent(ticker)}/?limit=${limit}`,
    { auth: false },
  );
}
