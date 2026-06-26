import os

import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


class ModelTrainer:

    def __init__(self, lstm_units=50, dropout_rate=0.2, epochs=50, batch_size=32):
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None

    # ── Build ────────────────────────────────────────────────────

    def build_model(self, input_shape):
        """Define and compile the LSTM architecture.

        Args:
            input_shape: (window_size, num_features) from X_train.shape[1:]
        """
        self.model = Sequential([
            LSTM(self.lstm_units, return_sequences=True, input_shape=input_shape),
            Dropout(self.dropout_rate),

            LSTM(self.lstm_units, return_sequences=False),
            Dropout(self.dropout_rate),

            Dense(25, activation='relu'),
            Dense(1),
        ])

        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return self.model

    # ── Train ────────────────────────────────────────────────────

    def train(self, X_train, y_train, X_test, y_test):
        """Train the model with early stopping.

        Returns the Keras History object (contains loss curves).
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model first.")

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
        )

        history = self.model.fit(
            X_train, y_train,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stop],
            verbose=1,
        )

        return history

    # ── Evaluate ─────────────────────────────────────────────────

    def evaluate(self, X_test, y_test):
        """Return test loss and MAE."""
        if self.model is None:
            raise ValueError("No model to evaluate.")
        return self.model.evaluate(X_test, y_test, verbose=0)

    # ── Persistence ──────────────────────────────────────────────

    def save_model(self, path):
        """Save trained model in .keras format."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)

    def load_model(self, path):
        """Load a previously saved model."""
        self.model = load_model(path)