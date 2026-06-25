from rest_framework import serializers

from .models import Stock, WatchlistItem


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'company_name', 'sector', 'exchange', 'is_active']


class WatchlistItemSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    symbol = serializers.CharField(write_only=True)

    class Meta:
        model = WatchlistItem
        fields = ['id', 'stock', 'symbol', 'added_at']
        read_only_fields = ['id', 'added_at']

    def validate_symbol(self, value):
        try:
            self.context['stock'] = Stock.objects.get(symbol=value.upper())
        except Stock.DoesNotExist:
            raise serializers.ValidationError(f'No stock found with symbol "{value.upper()}".')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        stock = self.context['stock']
        item, created = WatchlistItem.objects.get_or_create(user=user, stock=stock)
        self.context['created'] = created
        return item
