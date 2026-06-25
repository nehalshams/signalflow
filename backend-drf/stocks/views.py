from datetime import datetime

import yfinance as yf
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class StockDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ticker):
        years = int(request.query_params.get('years', 10))

        now = datetime.now()
        start = datetime(now.year - years, now.month, now.day)

        df = yf.download(ticker, start=start, end=now)

        if df.empty:
            return Response({'error': f'No data found for ticker "{ticker}"'}, status=404)

        df = df.reset_index()
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        data = [
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

        return Response({'ticker': ticker.upper(), 'count': len(data), 'data': data})
