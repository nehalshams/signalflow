"""Single place that talks to Yahoo Finance.

Keeps network/IO concerns out of the ML pipeline and the views so both can
share one cleaning path (reset index, flatten the MultiIndex columns yfinance
returns) and one failure mode.
"""
import logging
from datetime import datetime

import yfinance as yf

logger = logging.getLogger(__name__)


class DataFetchError(ValueError):
    """No usable data could be fetched for a ticker.

    Subclasses ValueError so existing ``except ValueError`` handlers in views
    and Celery tasks keep treating it as a recoverable/4xx condition.
    """


class DataFetchService:
    """Fetch OHLCV data as clean, flat DataFrames."""

    def fetch_history(self, ticker, years=10):
        """Fetch ``years`` of daily history for a ticker (for training)."""
        ticker = ticker.upper()
        now = datetime.now()
        start = datetime(now.year - years, now.month, now.day)
        logger.info('Fetching %d years of history for %s', years, ticker)
        df = yf.download(ticker, start=start, end=now, progress=False)
        return self._clean(df, ticker)

    def fetch_recent(self, ticker, period='200d'):
        """Fetch a recent window of daily data (for prediction)."""
        ticker = ticker.upper()
        logger.info('Fetching recent data (%s) for %s', period, ticker)
        df = yf.download(ticker, period=period, progress=False)
        return self._clean(df, ticker)

    # ── internal ─────────────────────────────────────────────────

    def _clean(self, df, ticker):
        if df is None or df.empty:
            raise DataFetchError(f'No data found for ticker "{ticker}"')

        df = df.reset_index()
        # yfinance can return MultiIndex columns ('Close', 'RELIANCE.NS') —
        # flatten to the first level.
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        logger.info('Fetched %d rows for %s', len(df), ticker)
        return df
