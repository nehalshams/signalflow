from celery.result import AsyncResult
from django.urls import reverse
from kombu.exceptions import OperationalError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Stock, WatchlistItem, StockPrice
from .serializers import StockSerializer, WatchlistItemSerializer, StockPriceSerializer
from .services import fetch_stock_prices, get_ohlcv_history, get_prediction, search_stocks
from .tasks import train_model_task


class StockSearchView(APIView):
    """GET /api/v1/stocks/search/?q=rel -> ranked matches with fuzzy fallback."""
    permission_classes = [AllowAny]

    def get(self, request):
        results = search_stocks(request.query_params.get('q', ''), limit=20)
        return Response(StockSerializer(results, many=True).data)


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
    """DELETE /api/v1/watchlist/<stock_id>/ -> remove a stock from my watchlist."""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return generics.get_object_or_404(
            WatchlistItem, user=self.request.user, stock_id=self.kwargs['stock_id']
        )


class StockDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ticker):
        years = int(request.query_params.get('years', 10))

        try:
            data = get_ohlcv_history(ticker, years=years)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({'ticker': ticker.upper(), 'count': len(data), 'data': data})


class StockPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            return Response(
                {'error': 'Stock not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        prices = StockPrice.objects.filter(stock=stock)
        if not prices.exists():
            fetch_stock_prices(symbol.upper())
            prices = StockPrice.objects.filter(stock=stock)

        period = request.query_params.get('period', '30')
        prices = prices[:int(period)]

        serializer = StockPriceSerializer(prices, many=True)
        return Response({
            'symbol': stock.symbol,
            'name': stock.company_name,
            'prices': serializer.data,
        })


class TrainModelView(APIView):
    """POST /api/v1/ml/train/<ticker>/ — queue an LSTM training job.

    Training takes minutes and is CPU-heavy, so it runs on a Celery worker
    rather than blocking the request. Returns 202 with a task id the client
    can poll via TrainStatusView.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, ticker):
        years = int(request.data.get('years', 10))

        try:
            task = train_model_task.delay(ticker, years)
        except OperationalError:
            # Broker (Redis) unreachable — can't accept the job right now.
            return Response(
                {'error': 'Training queue is unavailable. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                'message': f'Training queued for {ticker.upper()}',
                'ticker': ticker.upper(),
                'task_id': task.id,
                'status_url': reverse('train_status', args=[task.id]),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class TrainStatusView(APIView):
    """GET /api/v1/ml/train/status/<task_id>/ — poll a training job."""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        data = {'task_id': task_id, 'state': result.state}

        if result.successful():
            data['result'] = result.result
        elif result.failed():
            data['error'] = str(result.result)

        return Response(data)


class PredictView(APIView):
    """GET /api/v1/ml/predict/<ticker>/?days=30 — predict future prices."""
    permission_classes = [AllowAny]

    def get(self, request, ticker):
        forecast_days = int(request.query_params.get('days', 30))

        try:
            predictions, from_cache = get_prediction(ticker, forecast_days=forecast_days)
            return Response({
                'ticker': ticker.upper(),
                'forecast_days': forecast_days,
                'cached': from_cache,
                'predictions': predictions,
            })
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )