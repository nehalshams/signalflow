from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.symbol} - {self.company_name}'
