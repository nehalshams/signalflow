from django.contrib import admin

from .models import Stock, WatchlistItem, TrainingRun


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company_name', 'sector', 'is_active', 'updated_at')
    list_filter = ('sector', 'is_active')
    search_fields = ('symbol', 'company_name')


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'stock__symbol')


@admin.register(TrainingRun)
class TrainingRunAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'status', 'mape', 'rmse', 'mae', 'epochs_run', 'created_at')
    list_filter = ('status', 'ticker', 'created_at')
    search_fields = ('ticker',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
