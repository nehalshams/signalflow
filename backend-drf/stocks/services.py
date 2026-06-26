import logging
import os

import yfinance as yf
from django.conf import settings
from django.core.cache import cache

from ml_models.data_fetch import DataFetchService
from ml_models.pipeline import Pipeline

from .models import Stock, StockPrice

logger = logging.getLogger(__name__)

_data_fetcher = DataFetchService()


def get_ohlcv_history(ticker, years=10):
    """Return clean OHLCV rows for a ticker (for the StockDataView).

    Raises ml_models.data_fetch.DataFetchError (a ValueError) when no data
    is available.
    """
    df = _data_fetcher.fetch_history(ticker, years=years)
    return [
        {
            'date': row['Date'].strftime('%Y-%m-%d'),
            'open': round(row['Open'], 2),
            'high': round(row['High'], 2),
            'low': round(row['Low'], 2),
            'close': round(row['Close'], 2),
            'volume': int(row['Volume']),
        }
        for _, row in df.iterrows()
    ]


def get_prediction(ticker, forecast_days=30):
    """Return model predictions for a ticker, served from cache when possible.

    The cache key embeds the trained model's mtime, so retraining a ticker
    naturally invalidates its cached predictions. Returns
    ``(predictions, from_cache)``.
    """
    ticker = ticker.upper()
    pipeline = Pipeline()

    model_path, _ = pipeline.artifact_paths(ticker)
    try:
        model_version = int(os.path.getmtime(model_path))
    except OSError:
        # No model yet — let pipeline.predict raise FileNotFoundError below.
        model_version = 0

    cache_key = f'prediction:{ticker}:{forecast_days}:{model_version}'
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info('Prediction cache hit for %s (%d days)', ticker, forecast_days)
        return cached, True

    logger.info('Prediction cache miss for %s (%d days) — running model', ticker, forecast_days)
    predictions = pipeline.predict(ticker, forecast_days=forecast_days)
    cache.set(cache_key, predictions, timeout=settings.PREDICTION_CACHE_TTL)
    return predictions, False


def fetch_stock_prices(symbol, period='1y'):
    """
    Fetch stock prices from Yahoo Finance and save to database.
    For NSE stocks, Yahoo uses '.NS' suffix (e.g., RELIANCE.NS)
    """
    ticker = yf.Ticker(f"{symbol}.NS")
    data = ticker.history(period=period)

    if data.empty:
        return 0

    stock = Stock.objects.get(symbol=symbol)
    count = 0

    for date, row in data.iterrows():
        _, created = StockPrice.objects.update_or_create(
            stock=stock,
            date=date.date(),
            defaults={
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume']),
            }
        )
        if created:
            count += 1

    return count