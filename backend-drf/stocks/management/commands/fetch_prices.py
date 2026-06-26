from django.core.management.base import BaseCommand
from stocks.models import Stock
from stocks.services import fetch_stock_prices


class Command(BaseCommand):
    help = 'Fetch stock prices for all stocks'

    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        for stock in stocks:
            self.stdout.write(f"Fetching {stock.symbol}...")
            count = fetch_stock_prices(stock.symbol)
            self.stdout.write(f"  → {count} new prices saved")
        self.stdout.write(self.style.SUCCESS("Done!"))