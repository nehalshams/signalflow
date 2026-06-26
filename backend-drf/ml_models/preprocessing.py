import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessor:

    def __init__(self, window_size=60, test_ratio=0.2, target_column='Close'):
        self.window_size = window_size
        self.test_ratio = test_ratio
        self.target_column = target_column
        self.scaler = None
        self.target_col_index = None

    # ── Training time ────────────────────────────────────────────

    def fit_and_transform(self, df):
        """Scale, window and chronologically split a feature frame.

        The scaler is fit on the **training rows only** — never on the test
        period — so the reported test metrics aren't inflated by look-ahead
        leakage of the test set's min/max into the scaling.

        Returns (X_train, X_test, y_train, y_test).
        """
        # 0. keep only numeric feature columns (drops e.g. the Date column)
        df = self.numeric_features(df)

        # 1. remember which column is the target
        self.target_col_index = df.columns.get_loc(self.target_column)
        values = df.values

        # 2. decide the chronological split point in sequence space
        num_samples = len(values) - self.window_size
        if num_samples <= 0:
            raise ValueError(
                f"Need more than {self.window_size} rows to build sequences, "
                f"got {len(values)}."
            )
        split = int(num_samples * (1 - self.test_ratio))  # number of train samples

        # rows touched by the training samples run up to the last training
        # target row: sample (split-1) targets row (split-1 + window_size).
        train_rows_end = split + self.window_size

        # 3. fit scaler on training rows only, then transform everything
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.scaler.fit(values[:train_rows_end])
        scaled_data = self.scaler.transform(values)

        # 4. create sequences and split at the same chronological boundary
        X, y = self._create_sequences(scaled_data)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        return X_train, X_test, y_train, y_test

    # ── Prediction time ──────────────────────────────────────────

    def transform(self, df):
        """Scale incoming data using already-fitted scaler,
        return the last window as a single sample shaped (1, window_size, num_features)."""

        if self.scaler is None:
            raise ValueError("Scaler not fitted. Call fit_and_transform first or load a saved scaler.")

        df = self.numeric_features(df)
        scaled_data = self.scaler.transform(df.values)

        # take the last window_size rows as one input sample
        window = scaled_data[-self.window_size:]
        return window.reshape(1, self.window_size, -1)

    # ── Persistence ──────────────────────────────────────────────

    def save_scaler(self, path):
        """Save fitted scaler and metadata needed at prediction time."""
        joblib.dump({
            'scaler': self.scaler,
            'target_col_index': self.target_col_index,
            'window_size': self.window_size,
            'target_column': self.target_column,
        }, path)

    def load_scaler(self, path):
        """Load a previously saved scaler and restore metadata."""
        bundle = joblib.load(path)
        self.scaler = bundle['scaler']
        self.target_col_index = bundle['target_col_index']
        self.window_size = bundle['window_size']
        self.target_column = bundle['target_column']

    # ── Private helpers ──────────────────────────────────────────

    @staticmethod
    def numeric_features(df):
        """Keep only numeric feature columns so the scaler never sees
        non-numeric data such as the Date column produced by reset_index()."""
        return df.select_dtypes(include=[np.number])

    def _create_sequences(self, data):
        """Slide a window across the scaled 2D array.

        For each position i the input is data[i : i+window_size] (all features)
        and the target is data[i+window_size, target_col_index] (next day's close).

        Returns:
            X  – shape (num_samples, window_size, num_features)
            y  – shape (num_samples,)
        """
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i: i + self.window_size])
            y.append(data[i + self.window_size, self.target_col_index])

        return np.array(X), np.array(y)