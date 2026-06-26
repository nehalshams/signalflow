import numpy as np
import pandas as pd

from .features import FeatureEngineer
from .preprocessing import DataPreprocessor
from .trainer import ModelTrainer


class Predictor:
    """Load a trained model + scaler and produce predictions."""

    def __init__(self, model_path, scaler_path):
        self.trainer = ModelTrainer()
        self.trainer.load_model(model_path)

        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_scaler(scaler_path)

        self.feature_engineer = FeatureEngineer()

    def predict(self, raw_df, forecast_days=1):
        """Predict next N days' closing prices.

        Multi-day forecasting is recursive: after each predicted close we
        extend the raw history with a synthetic next-day bar and recompute
        the full technical-indicator set. This keeps RSI / MACD / Bollinger /
        volume features consistent with the predicted price path, rather than
        freezing them at the last observed value (which makes longer-horizon
        forecasts reason over stale, inconsistent inputs).

        Args:
            raw_df:  raw OHLCV DataFrame (needs enough rows for features + window)
            forecast_days: how many days ahead to predict

        Returns:
            list of dicts with day number and predicted close price
        """
        window_size = self.preprocessor.window_size
        target_idx = self.preprocessor.target_col_index
        num_features = self.preprocessor.scaler.n_features_in_

        # working copy of the raw history we extend as we forecast
        working_df = raw_df.copy()

        # up-front sanity check on available history
        if len(self.feature_engineer.add_all_features(working_df)) < window_size:
            raise ValueError(
                f"Need at least {window_size} rows after feature engineering."
            )

        predictions = []
        for day in range(1, forecast_days + 1):
            # recompute indicators over the (growing) history each step
            featured_df = self.feature_engineer.add_all_features(working_df)
            featured_df = self.preprocessor.numeric_features(featured_df)
            scaled = self.preprocessor.scaler.transform(featured_df.values)
            window = scaled[-window_size:]

            X_input = window.reshape(1, window_size, num_features)
            pred_scaled = self.trainer.model.predict(X_input, verbose=0)[0, 0]
            pred_price = self._inverse_scale(pred_scaled, target_idx, num_features)

            predictions.append({
                'day': day,
                'predicted_close': round(float(pred_price), 2),
            })

            # extend history with a synthetic bar so the next step's
            # indicators reflect the just-predicted close
            working_df = self._append_forecast_bar(working_df, pred_price)

        return predictions

    def _append_forecast_bar(self, df, close):
        """Append a synthetic next-day OHLCV row from a predicted close.

        Only the close is forecast, so O/H/L are set to it and volume to the
        recent average — enough to keep indicators evolving consistently with
        the predicted price on subsequent steps.
        """
        new_row = df.iloc[-1].to_dict()

        for col in ('Open', 'High', 'Low', 'Close'):
            if col in new_row:
                new_row[col] = close
        if 'Volume' in new_row:
            new_row['Volume'] = float(df['Volume'].tail(20).mean())
        if 'Date' in new_row:
            new_row['Date'] = df.iloc[-1]['Date'] + pd.Timedelta(days=1)

        return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    def _inverse_scale(self, scaled_value, target_idx, num_features):
        """Convert a single scaled Close value back to original price."""
        dummy = np.zeros((1, num_features))
        dummy[0, target_idx] = scaled_value
        inverted = self.preprocessor.scaler.inverse_transform(dummy)
        return inverted[0, target_idx]