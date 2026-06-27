from rest_framework import serializers

from .models import Stock, WatchlistItem, StockPrice, TrainingRun

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'company_name', 'sector', 'exchange', 'is_active']


class WatchlistItemSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), write_only=True
    )

    class Meta:
        model = WatchlistItem
        fields = ['id', 'stock', 'stock_id', 'added_at']
        read_only_fields = ['id', 'added_at']

    def create(self, validated_data):
        user = self.context['request'].user
        stock = validated_data['stock_id']
        item, created = WatchlistItem.objects.get_or_create(user=user, stock=stock)
        self.context['created'] = created
        return item

class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['date', 'open', 'high', 'low', 'close', 'volume']


class TrainingRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingRun
        fields = [
            'id', 'ticker', 'status',
            'rmse', 'mae', 'mape', 'mse',
            'epochs_run', 'training_samples', 'test_samples',
            'notes', 'created_at',
        ]




