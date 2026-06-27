from django.urls import path
from accounts import views as UserViews
from stocks import views as StockViews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register', UserViews.RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserViews.LogoutView.as_view(), name='logout'),

    path('protected-view/', UserViews.ProtectedView.as_view()),

    path('stocks/search/', StockViews.StockSearchView.as_view()),

    path('watchlist/', StockViews.WatchlistView.as_view()),
    path('watchlist/<int:stock_id>/', StockViews.WatchlistItemDeleteView.as_view()),

    path('stocks/<str:ticker>/', StockViews.StockDataView.as_view()),

    # stock prices
    path('stocks/<str:symbol>/prices/', StockViews.StockPriceView.as_view(), name='stock_prices'),

    # ML endpoints
    path('ml/train/status/<str:task_id>/', StockViews.TrainStatusView.as_view(), name='train_status'),
    path('ml/train/<str:ticker>/', StockViews.TrainModelView.as_view(), name='train_model'),
    path('ml/predict/<str:ticker>/', StockViews.PredictView.as_view(), name='predict'),
    path('ml/training-runs/<str:ticker>/', StockViews.TrainingRunsView.as_view(), name='training_runs'),
]