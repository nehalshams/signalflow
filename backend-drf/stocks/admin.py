from django.contrib import admin

from .models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company_name', 'sector', 'is_active', 'updated_at')
    list_filter = ('sector', 'is_active')
    search_fields = ('symbol', 'company_name')
