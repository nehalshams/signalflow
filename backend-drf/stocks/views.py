from datetime import datetime

import yfinance as yf
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Stock, WatchlistItem
from .serializers import StockSerializer, WatchlistItemSerializer


class StockSearchView(generics.ListAPIView):
    """GET /api/v1/stocks/search/?q=rel -> stocks matching symbol or company name."""
    serializer_class = StockSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        qs = Stock.objects.filter(is_active=True)
        if not query:
            return qs.none()
        return qs.filter(Q(symbol__icontains=query) | Q(company_name__icontains=query))


class WatchlistView(generics.ListCreateAPIView):
    """GET -> my watchlist; POST {"symbol": "RELIANCE"} -> add to watchlist."""
    serializer_class = WatchlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user).select_related('stock')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        created = serializer.context.get('created', False)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class WatchlistItemDeleteView(generics.DestroyAPIView):
    """DELETE /api/v1/watchlist/<symbol>/ -> remove a stock from my watchlist."""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        symbol = self.kwargs['symbol'].upper()
        return generics.get_object_or_404(
            WatchlistItem, user=self.request.user, stock__symbol=symbol
        )


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
