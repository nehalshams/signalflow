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