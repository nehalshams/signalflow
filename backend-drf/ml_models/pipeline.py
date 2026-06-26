import logging
import os
import sys

from .data_fetch import DataFetchService
from .features import FeatureEngineer
from .preprocessing import DataPreprocessor
from .trainer import ModelTrainer
from .predict import Predictor

logger = logging.getLogger(__name__)


SAVED_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'saved_models',
)


class Pipeline:
    """Orchestrates the full ML workflow."""

    def __init__(
        self,
        sma_windows=(20, 50),
        rsi_period=14,
        bb_window=20,
        window_size=60,
        test_ratio=0.2,
        lstm_units=(50, 50),
        dropout_rate=0.2,
        learning_rate=0.001,
        epochs=50,
        batch_size=32,
        save_dir=SAVED_MODELS_DIR,
    ):
        self.feature_engineer = FeatureEngineer(
            sma_windows=sma_windows,
            rsi_period=rsi_period,
            bb_window=bb_window,
        )
        self.preprocessor = DataPreprocessor(
            window_size=window_size,
            test_ratio=test_ratio,
        )
        self.trainer = ModelTrainer(
            lstm_units=lstm_units,
            dropout_rate=dropout_rate,
            learning_rate=learning_rate,
            epochs=epochs,
            batch_size=batch_size,
        )
        self.data_fetcher = DataFetchService()
        self.save_dir = save_dir

    # ── Training ─────────────────────────────────────────────────

    def train(self, ticker, years=10):
        """Full training pipeline for a single ticker.

        Args:
            ticker: e.g. 'RELIANCE.NS'
            years:  how many years of history to fetch

        Returns:
            dict with metrics and file paths
        """
        ticker = ticker.upper()

        # 1. fetch raw data
        df = self.data_fetcher.fetch_history(ticker, years=years)
        logger.info('[1/5] Fetched %d rows for %s', len(df), ticker)

        # 2. feature engineering
        df = self.feature_engineer.add_all_features(df)
        logger.info('[2/5] Features computed — %d rows remain after NaN drop', len(df))

        # 3. preprocessing — scale, window, split
        X_train, X_test, y_train, y_test = self.preprocessor.fit_and_transform(df)
        logger.info('[3/5] Sequences created — train: %d, test: %d', len(X_train), len(X_test))

        # 4. build and train
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.trainer.build_model(input_shape)
        self.trainer.model.summary(print_fn=logger.info)
        logger.info('[4/5] Training started ...')
        history = self.trainer.train(X_train, y_train, X_test, y_test)

        # 5. evaluate and save
        metrics = self.trainer.evaluate(
            X_test, y_test,
            self.preprocessor.scaler,
            self.preprocessor.target_col_index,
        )
        logger.info(
            '[5/5] Evaluation — RMSE: %s, MAE: %s, MAPE: %s%%',
            metrics['rmse'], metrics['mae'], metrics['mape'],
        )

        model_path, scaler_path = self._save_artifacts(ticker)

        return {
            'ticker': ticker,
            'metrics': metrics,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'epochs_run': len(history.history['loss']),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
        }

    # ── Prediction ───────────────────────────────────────────────

    def predict(self, ticker, forecast_days=30):
        """Predict future prices using saved model.

        Args:
            ticker: must match a previously trained ticker
            forecast_days: how many days to forecast

        Returns:
            list of dicts with day and predicted_close
        """
        ticker = ticker.upper()
        model_path, scaler_path = self.artifact_paths(ticker)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No trained model found for {ticker} at {model_path}")

        # fetch recent data — enough for features + window
        df = self.data_fetcher.fetch_recent(ticker, period='200d')

        predictor = Predictor(model_path, scaler_path)
        return predictor.predict(df, forecast_days=forecast_days)

    # ── Helpers ──────────────────────────────────────────────────

    def artifact_paths(self, ticker):
        """Return (model_path, scaler_path) for a ticker's saved artifacts."""
        ticker_dir = os.path.join(self.save_dir, ticker.upper())
        model_path = os.path.join(ticker_dir, 'model.keras')
        scaler_path = os.path.join(ticker_dir, 'scaler.joblib')
        return model_path, scaler_path

    def _save_artifacts(self, ticker):
        model_path, scaler_path = self.artifact_paths(ticker)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.trainer.save_model(model_path)
        self.preprocessor.save_scaler(scaler_path)
        logger.info('Model saved to %s', model_path)
        logger.info('Scaler saved to %s', scaler_path)
        return model_path, scaler_path


# ── CLI entry point ──────────────────────────────────────────────

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'RELIANCE.NS'
    pipeline = Pipeline()
    result = pipeline.train(ticker)
    logger.info('Result: %s', result)