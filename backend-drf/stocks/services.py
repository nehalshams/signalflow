import yfinance as yf
from .models import Stock, StockPrice


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