from typing import List

import numpy as np
import yfinance as yf

from .features import add_all_features
from .preprocessing import (
    FEATURE_COLS,
    CLOSE_INDEX,
    load_scaler,
)
from .trainer import load_trained_model


def predict_future(
    ticker,
    model_path,
    scaler_path,
    look_back=60,
    forecast_days=30,
):
    # 4b — Load model and scaler
    model = load_trained_model(model_path)
    scaler = load_scaler(scaler_path)

    # 4c — Fetch recent data and compute indicators
    fetch_days = look_back + 100
    df = yf.download(ticker, period=f'{fetch_days}d')

    if df.empty:
        raise ValueError(f'No data found for ticker "{ticker}"')

    df = df.reset_index()
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df = add_all_features(df)

    # 4d — Scale and seed the window
    data = df[FEATURE_COLS].values
    scaled_data = scaler.transform(data)
    current_window = scaled_data[-look_back:].copy()

    # 4e — Predict day by day
    predictions = []
    for day in range(1, forecast_days + 1):
        X_input = current_window.reshape(1, look_back, len(FEATURE_COLS))
        pred_scaled = model.predict(X_input, verbose=0)[0, 0]

        dummy = np.zeros((1, len(FEATURE_COLS)))
        dummy[0, CLOSE_INDEX] = pred_scaled
        pred_price = scaler.inverse_transform(dummy)[0, CLOSE_INDEX]

        predictions.append({
            'day': day,
            'predicted_close': round(float(pred_price), 2),
        })

        new_row = current_window[-1].copy()
        new_row[CLOSE_INDEX] = pred_scaled
        current_window = np.vstack([current_window[1:], new_row])

    return predictions


