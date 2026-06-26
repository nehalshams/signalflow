import os

import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


class ModelTrainer:

    def __init__(self, lstm_units=(50, 50), dropout_rate=0.2,
                 learning_rate=0.001, epochs=50, batch_size=32):
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None

    # ── Build ────────────────────────────────────────────────────

    def build_model(self, input_shape):
        """Build and compile the LSTM.

        Args:
            input_shape: (window_size, num_features) from X_train.shape[1:]
        """
        self.model = Sequential()
        self.model.add(Input(shape=input_shape))

        for i, units in enumerate(self.lstm_units):
            return_seq = i < len(self.lstm_units) - 1
            self.model.add(LSTM(units, return_sequences=return_seq))
            self.model.add(Dropout(self.dropout_rate))

        self.model.add(Dense(25, activation='relu'))
        self.model.add(Dense(1))

        self.model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae'],
        )
        return self.model

    # ── Train ────────────────────────────────────────────────────

    def train(self, X_train, y_train, X_test, y_test):
        """Train with early stopping and learning rate reduction."""
        if self.model is None:
            raise ValueError("Model not built. Call build_model first.")

        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
            ),
        ]

        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1,
        )
        return history

    # ── Evaluate ─────────────────────────────────────────────────

    def evaluate(self, X_test, y_test, scaler, target_col_index):
        """Evaluate with inverse-scaled metrics (RMSE, MAE, MAPE)."""
        predictions_scaled = self.model.predict(X_test, verbose=0).flatten()

        num_features = scaler.n_features_in_
        dummy = np.zeros((len(predictions_scaled), num_features))

        # inverse-transform predictions
        dummy[:, target_col_index] = predictions_scaled
        pred_prices = scaler.inverse_transform(dummy)[:, target_col_index]

        # inverse-transform actuals
        dummy[:, target_col_index] = y_test
        actual_prices = scaler.inverse_transform(dummy)[:, target_col_index]

        mse = float(np.mean((pred_prices - actual_prices) ** 2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(pred_prices - actual_prices)))

        mask = actual_prices != 0
        mape = float(np.mean(np.abs(
            (actual_prices[mask] - pred_prices[mask]) / actual_prices[mask]
        )) * 100)

        return {
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'mae': round(mae, 4),
            'mape': round(mape, 4),
        }

    # ── Persistence ──────────────────────────────────────────────

    def save_model(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)

    def load_model(self, path):
        self.model = load_model(path)