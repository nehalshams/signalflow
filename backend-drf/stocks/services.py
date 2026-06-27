import logging
import os

import yfinance as yf
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.db import DatabaseError
from django.db.models import Case, IntegerField, Q, Value, When

from ml_models.data_fetch import DataFetchService
from ml_models.pipeline import Pipeline

from .models import Stock, StockPrice, TrainingRun

logger = logging.getLogger(__name__)

_data_fetcher = DataFetchService()

# Minimum trigram similarity for a fuzzy suggestion to be offered.
_FUZZY_THRESHOLD = 0.2


def search_stocks(query, limit=20):
    """Search the stock universe, returning the best matches for ``query``.

    Two tiers:
      1. Substring matches on symbol/company name, ranked exact → prefix →
         contains so the most relevant hit is first.
      2. If nothing matches as a substring (e.g. a typo), fall back to
         trigram similarity so we still surface close suggestions instead of
         an empty result.
    """
    query = (query or "").strip()
    if not query:
        return []

    base = Stock.objects.filter(is_active=True)

    substring = (
        base.filter(Q(symbol__icontains=query) | Q(company_name__icontains=query))
        .annotate(
            match_rank=Case(
                When(symbol__iexact=query, then=Value(0)),
                When(symbol__istartswith=query, then=Value(1)),
                When(symbol__icontains=query, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .order_by("match_rank", "symbol")[:limit]
    )
    results = list(substring)
    if results:
        return results

    # Tier 2 — fuzzy suggestions. Guard against the extension being missing.
    try:
        fuzzy = (
            base.annotate(
                similarity=TrigramSimilarity("company_name", query)
                + TrigramSimilarity("symbol", query)
            )
            .filter(similarity__gt=_FUZZY_THRESHOLD)
            .order_by("-similarity")[:limit]
        )
        return list(fuzzy)
    except DatabaseError:
        logger.warning("Trigram search unavailable; returning no suggestions for %r", query)
        return []

# A retrain whose MAPE is more than this fraction worse than the previous
# good run is flagged as drift (e.g. 0.25 = 25% relative degradation).
DRIFT_MAPE_RELATIVE_THRESHOLD = float(
    os.environ.get('DRIFT_MAPE_RELATIVE_THRESHOLD', '0.25')
)


def record_training_run(ticker, result):
    """Persist a successful training run and flag drift vs. the last good run.

    Returns the created TrainingRun. Its ``status`` is ``degraded`` when the
    new MAPE is materially worse than the previous non-failed run for the same
    ticker, otherwise ``success``.
    """
    metrics = result['metrics']

    previous = (
        TrainingRun.objects
        .filter(ticker=ticker, mape__isnull=False)
        .exclude(status=TrainingRun.STATUS_FAILED)
        .order_by('-created_at')
        .first()
    )

    status = TrainingRun.STATUS_SUCCESS
    notes = ''
    if previous and previous.mape:
        relative_change = (metrics['mape'] - previous.mape) / previous.mape
        if relative_change > DRIFT_MAPE_RELATIVE_THRESHOLD:
            status = TrainingRun.STATUS_DEGRADED
            notes = (
                f'MAPE {metrics["mape"]:.3f}% is {relative_change * 100:.1f}% worse '
                f'than previous {previous.mape:.3f}% (run #{previous.id}).'
            )

    return TrainingRun.objects.create(
        ticker=ticker,
        status=status,
        rmse=metrics['rmse'],
        mae=metrics['mae'],
        mape=metrics['mape'],
        mse=metrics['mse'],
        epochs_run=result.get('epochs_run'),
        training_samples=result.get('training_samples'),
        test_samples=result.get('test_samples'),
        notes=notes,
    )


def record_training_failure(ticker, error):
    """Persist a failed training run so failures aren't silent."""
    return TrainingRun.objects.create(
        ticker=ticker,
        status=TrainingRun.STATUS_FAILED,
        notes=str(error)[:2000],
    )


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

    # Cache is an optimization, not a hard dependency — if Redis is down we
    # still serve a freshly computed prediction rather than failing the request.
    try:
        cached = cache.get(cache_key)
    except Exception:  # noqa: BLE001 — degrade gracefully on any cache backend error
        logger.warning('Prediction cache unavailable (read) for %s; computing fresh', ticker)
        cached = None

    if cached is not None:
        logger.info('Prediction cache hit for %s (%d days)', ticker, forecast_days)
        return cached, True

    logger.info('Prediction cache miss for %s (%d days) — running model', ticker, forecast_days)
    predictions = pipeline.predict(ticker, forecast_days=forecast_days)

    try:
        cache.set(cache_key, predictions, timeout=settings.PREDICTION_CACHE_TTL)
    except Exception:  # noqa: BLE001
        logger.warning('Prediction cache unavailable (write) for %s', ticker)

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