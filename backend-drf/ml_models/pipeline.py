import os

import pandas as pd

from .features import FeatureEngineer
from .preprocessing import DataPreprocessor
from .trainer import ModelTrainer
from .predict import Predictor


# default directory for saved models and scalers
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')


class Pipeline:
    """Orchestrates the full ML workflow: feature engineering → preprocessing → training → prediction."""

    def __init__(
        self,
        sma_windows=(20, 50),
        rsi_period=14,
        bb_window=20,
        window_size=60,
        test_ratio=0.2,
        lstm_units=50,
        dropout_rate=0.2,
        epochs=50,
        batch_size=32,
        model_dir=DEFAULT_MODEL_DIR,
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
            epochs=epochs,
            batch_size=batch_size,
        )
        self.model_dir = model_dir

    # ── Training ─────────────────────────────────────────────────

    def train(self, raw_df, ticker):
        """Full training pipeline for a single ticker.

        Args:
            raw_df:  DataFrame with Date, Open, High, Low, Close, Volume
            ticker:  e.g. 'RELIANCE' — used for naming saved files

        Returns:
            dict with training metrics and file paths
        """
        # 1. feature engineering
        featured_df = self.feature_engineer.add_all_features(raw_df)

        # 2. preprocessing — fit scaler, create sequences, split
        X_train, X_test, y_train, y_test = self.preprocessor.fit_and_transform(featured_df)

        # 3. build and train
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.trainer.build_model(input_shape)
        history = self.trainer.train(X_train, y_train, X_test, y_test)

        # 4. evaluate
        test_loss, test_mae = self.trainer.evaluate(X_test, y_test)

        # 5. save model and scaler
        model_path, scaler_path = self._save_artifacts(ticker)

        return {
            'ticker': ticker,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'test_loss': round(test_loss, 6),
            'test_mae': round(test_mae, 6),
            'epochs_run': len(history.history['loss']),
            'samples': {
                'train': len(X_train),
                'test': len(X_test),
            },
        }

    # ── Prediction ───────────────────────────────────────────────

    def predict(self, raw_df, ticker):
        """Run prediction for a ticker using saved model and scaler.

        Args:
            raw_df:  recent OHLCV DataFrame (needs at least window_size + warmup rows)
            ticker:  must match a previously trained ticker

        Returns:
            predicted next-day closing price as float
        """
        model_path, scaler_path = self._artifact_paths(ticker)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No trained model found for {ticker} at {model_path}")

        # feature engineering on the incoming data
        featured_df = self.feature_engineer.add_all_features(raw_df)

        # load model + scaler and predict
        predictor = Predictor(model_path, scaler_path)
        return predictor.predict(featured_df)

    # ── Helpers ──────────────────────────────────────────────────

    def _artifact_paths(self, ticker):
        ticker_dir = os.path.join(self.model_dir, ticker.upper())
        model_path = os.path.join(ticker_dir, 'model.keras')
        scaler_path = os.path.join(ticker_dir, 'scaler.joblib')
        return model_path, scaler_path

    def _save_artifacts(self, ticker):
        model_path, scaler_path = self._artifact_paths(ticker)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.trainer.save_model(model_path)
        self.preprocessor.save_scaler(scaler_path)
        return model_path, scaler_path