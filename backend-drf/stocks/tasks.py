"""Celery tasks for automated model training.

The daily retrain is dispatched by Celery Beat (see CELERY_BEAT_SCHEDULE in
settings) which calls ``retrain_all_active_models``; that fans out one
``train_model_task`` per active stock so a single slow/failed ticker never
blocks the rest.
"""
import logging

from celery import shared_task

from ml_models.pipeline import Pipeline

logger = logging.getLogger(__name__)


# Yahoo Finance suffixes per exchange. Stock.symbol is stored bare
# (e.g. "RELIANCE"); yfinance needs the exchange suffix ("RELIANCE.NS").
_EXCHANGE_SUFFIX = {
    'NSE': '.NS',
    'BSE': '.BO',
}


def to_yf_ticker(symbol, exchange='NSE'):
    """Map a stored stock symbol + exchange to a Yahoo Finance ticker."""
    return f'{symbol}{_EXCHANGE_SUFFIX.get(exchange, "")}'


@shared_task(
    bind=True,
    name='stocks.tasks.train_model_task',
    max_retries=3,
    default_retry_delay=300,  # 5 min — yfinance rate-limits are transient
)
def train_model_task(self, ticker, years=10):
    """Train an LSTM model for a single Yahoo Finance ticker.

    Args:
        ticker: full yfinance ticker, e.g. "RELIANCE.NS"
        years:  years of history to train on
    """
    # Imported here so the module loads even before Django apps are ready.
    from stocks.models import TrainingRun
    from stocks.services import record_training_run, record_training_failure

    logger.info('Training model for %s (%d years)', ticker, years)
    try:
        result = Pipeline().train(ticker, years=years)
    except ValueError as exc:
        # Most often a transient "no data found" from Yahoo — retry.
        logger.warning('Training %s failed (%s); retrying', ticker, exc)
        raise self.retry(exc=exc)
    except Exception as exc:  # noqa: BLE001 — record then let Celery mark failed
        record_training_failure(ticker, exc)
        logger.exception('Training %s failed permanently', ticker)
        raise

    run = record_training_run(ticker, result)
    if run.status == TrainingRun.STATUS_DEGRADED:
        logger.warning('MODEL DRIFT for %s — %s', ticker, run.notes)

    logger.info(
        'Trained %s — metrics=%s (run #%s, %s)',
        ticker, result['metrics'], run.id, run.status,
    )
    return {
        'ticker': result['ticker'],
        'metrics': result['metrics'],
        'epochs_run': result['epochs_run'],
        'training_samples': result['training_samples'],
        'test_samples': result['test_samples'],
        'run_id': run.id,
        'status': run.status,
    }


@shared_task(name='stocks.tasks.retrain_all_active_models')
def retrain_all_active_models(years=10):
    """Fan out a training task for every active stock.

    Run daily by Celery Beat at 08:30 IST.

    Each ticker is trained by an independent ``train_model_task``, so one
    ticker failing (bad symbol, delisted, training error) never blocks the
    others. We also guard the dispatch loop itself so a single bad row can't
    abort the whole batch.
    """
    # Imported lazily so the module loads even before Django apps are ready.
    from stocks.models import Stock

    stocks = Stock.objects.filter(is_active=True).values_list('symbol', 'exchange')

    dispatched, failed = [], []
    for symbol, exchange in stocks:
        try:
            ticker = to_yf_ticker(symbol, exchange)
            train_model_task.delay(ticker, years)
            dispatched.append(ticker)
        except Exception:  # noqa: BLE001 — never let one bad row stop the rest
            logger.exception('Failed to dispatch training for %s (%s)', symbol, exchange)
            failed.append(symbol)

    logger.info(
        'Retrain dispatch complete — %d queued, %d failed to queue',
        len(dispatched), len(failed),
    )
    return {'dispatched': dispatched, 'failed': failed, 'count': len(dispatched)}
