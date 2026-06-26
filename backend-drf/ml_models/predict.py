import numpy as np

from .preprocessing import DataPreprocessor
from .trainer import ModelTrainer


class Predictor:
    """Load a trained model + scaler and produce predictions from raw featured data."""

    def __init__(self, model_path, scaler_path):
        self.trainer = ModelTrainer()
        self.trainer.load_model(model_path)

        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_scaler(scaler_path)

    def predict(self, featured_df):
        """Take a featured DataFrame (output of FeatureEngineer.add_all_features),
        return the predicted next-day closing price as a float.

        The DataFrame must have at least window_size rows.
        """
        window_size = self.preprocessor.window_size

        if len(featured_df) < window_size:
            raise ValueError(
                f"Need at least {window_size} rows, got {len(featured_df)}."
            )

        # scale and shape into (1, window_size, num_features)
        X = self.preprocessor.transform(featured_df)

        # model predicts a scaled value
        scaled_prediction = self.trainer.model.predict(X, verbose=0)

        # inverse-transform to get the real price
        actual_price = self._inverse_scale(scaled_prediction[0, 0])
        return round(float(actual_price), 2)

    def _inverse_scale(self, scaled_value):
        """Convert a single scaled Close prediction back to the original price.

        The scaler was fitted on all feature columns together, so to invert
        just the target column we reconstruct a dummy row with the scaled value
        in the correct column position and invert the whole row.
        """
        scaler = self.preprocessor.scaler
        target_idx = self.preprocessor.target_col_index
        num_features = scaler.n_features_in_

        # build a dummy row of zeros, place the scaled value in the target column
        dummy = np.zeros((1, num_features))
        dummy[0, target_idx] = scaled_value

        # inverse transform and extract the target column
        inverted = scaler.inverse_transform(dummy)
        return inverted[0, target_idx]