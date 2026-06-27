from django.conf import settings
from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    exchange = models.CharField(max_length=50, default='NSE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.symbol} - {self.company_name}'


class WatchlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlist',
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='watched_by',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'stock'],
                name='unique_user_stock_watchlist',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.stock.symbol}'



class TrainingRun(models.Model):
    """A record of one model-training run and its evaluation metrics.

    Persisting every run gives the daily Celery retrain an audit trail and
    lets us flag drift — when a fresh model evaluates noticeably worse than
    the last good one — instead of silently overwriting a healthy model.
    """
    STATUS_SUCCESS = 'success'
    STATUS_DEGRADED = 'degraded'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_DEGRADED, 'Degraded (possible drift)'),
        (STATUS_FAILED, 'Failed'),
    ]

    # full yfinance ticker, e.g. "RELIANCE.NS"
    ticker = models.CharField(max_length=30, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)

    # evaluation metrics — null when the run failed before evaluation
    rmse = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    mape = models.FloatField(null=True, blank=True)
    mse = models.FloatField(null=True, blank=True)

    epochs_run = models.IntegerField(null=True, blank=True)
    training_samples = models.IntegerField(null=True, blank=True)
    test_samples = models.IntegerField(null=True, blank=True)

    # drift details on a degraded run, or the error message on a failed run
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['ticker', '-created_at'])]

    def __str__(self):
        return f'{self.ticker} @ {self.created_at:%Y-%m-%d %H:%M} [{self.status}]'


class StockPrice(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='prices'
    )
    date = models.DateField()
    open = models.DecimalField(max_digits=12, decimal_places=2)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    close = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - {self.close}"