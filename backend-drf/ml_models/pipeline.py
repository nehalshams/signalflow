import os
import sys
from datetime import datetime

import yfinance as yf

from .features import add_all_features
from .preprocessing import (
    FEATURE_COLS,
    scale_data,
    create_sequences,
    train_test_split,
    save_scaler,
)
from .trainer import (
    build_model,
    train_model,
    evaluate_model,
    save_trained_model,
)


SAVED_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'saved_models',
)



def run_training_pipeline(
    ticker,
    years=10,
    look_back=60,
    epochs=50,
    batch_size=32,
    test_ratio=0.2,
    save_dir=SAVED_MODELS_DIR,
):
    ticker = ticker.upper()

    # ── Stage 1: Fetch raw OHLCV data from Yahoo Finance ─────
    now = datetime.now()
    start = datetime(now.year - years, now.month, now.day)
    df = yf.download(ticker, start=start, end=now)

    if df.empty:
        raise ValueError(f'No data found for ticker "{ticker}"')

    df = df.reset_index()
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    print(f'[1/5] Fetched {len(df)} rows for {ticker}')

    # ── Stage 2: Compute technical indicators ────────────────
    df = add_all_features(df)
    print(f'[2/5] Features computed — {len(df)} rows remain after NaN drop')

    # ── Stage 3: Scale, create sequences, split ──────────────
    scaled_data, scaler = scale_data(df)
    X, y = create_sequences(scaled_data, look_back=look_back)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_ratio=test_ratio)
    print(f'[3/5] Sequences created — train: {len(X_train)}, test: {len(X_test)}')

    # ── Stage 4: Build and train the LSTM ────────────────────
    n_features = X_train.shape[2]
    model = build_model(look_back=look_back, n_features=n_features)
    model.summary()
    print(f'[4/5] Training started ...')
    train_model(model, X_train, y_train, X_test, y_test,
                epochs=epochs, batch_size=batch_size)

    # ── Stage 5: Evaluate and save ───────────────────────────
    metrics = evaluate_model(model, X_test, y_test, scaler)
    print(f'[5/5] Evaluation — RMSE: {metrics["rmse"]}, MAE: {metrics["mae"]}, MAPE: {metrics["mape"]}%')

    ticker_dir = os.path.join(save_dir, ticker)
    model_path = os.path.join(ticker_dir, 'model.keras')
    scaler_path = os.path.join(ticker_dir, 'scaler.pkl')

    save_trained_model(model, model_path)
    save_scaler(scaler, scaler_path)

    print(f'Model saved to {model_path}')
    print(f'Scaler saved to {scaler_path}')

    return {
        'ticker': ticker,
        'metrics': metrics,
        'model_path': model_path,
        'scaler_path': scaler_path,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
    }


if __name__ == '__main__':
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'RELIANCE.NS'
    result = run_training_pipeline(ticker)
    print('\nResult:', result)


    