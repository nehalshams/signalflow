import os
from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Sequential — a linear stack of layers, simplest way to build a model
# LSTM — the recurrent layer that understands sequences
# Dense — regular fully connected layer
# Dropout — randomly disables neurons during training to prevent overfitting
# Input — explicitly defines the input shape
# EarlyStopping — stops training when the model stops improving
# ReduceLROnPlateau — lowers the learning rate when progress stalls
# Adam — the optimizer that adjusts weights during training


def build_model(
    look_back,
    n_features,
    lstm_units=(50, 50),
    dropout_rate=0.2,
    learning_rate=0.001,
):
    model = Sequential()

    model.add(Input(shape=(look_back, n_features)))

    for i, units in enumerate(lstm_units):
        return_seq = i < len(lstm_units) - 1
        model.add(LSTM(units, return_sequences=return_seq))
        model.add(Dropout(dropout_rate))

    model.add(Dense(25, activation='relu'))
    model.add(Dense(1))

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=['mae'],
    )

    return model


def train_model(model, X_train, y_train, X_test, y_test, epochs=50, batch_size=32):
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

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    return history


def evaluate_model(model, X_test, y_test, scaler):
    from .preprocessing import FEATURE_COLS, CLOSE_INDEX

    predictions_scaled = model.predict(X_test, verbose=0).flatten()

    # Inverse-transform requires a full-width array (all 26 columns)
    # We only have the Close column, so we build a dummy array
    n_features = len(FEATURE_COLS)
    dummy = np.zeros((len(predictions_scaled), n_features))

    dummy[:, CLOSE_INDEX] = predictions_scaled
    pred_prices = scaler.inverse_transform(dummy)[:, CLOSE_INDEX]

    dummy[:, CLOSE_INDEX] = y_test
    actual_prices = scaler.inverse_transform(dummy)[:, CLOSE_INDEX]

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



def save_trained_model(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model.save(path)

def load_trained_model(path):
    return load_model(path)