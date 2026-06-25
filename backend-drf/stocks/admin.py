from django.contrib import admin

from .models import Stock, WatchlistItem


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
