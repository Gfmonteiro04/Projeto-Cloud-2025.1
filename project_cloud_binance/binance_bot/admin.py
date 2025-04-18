from django.contrib import admin
from .models import TradeOrder

@admin.register(TradeOrder)
class TradeOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', 'order_type', 'price', 'quantity', 'status', 'created_at')
    search_fields = ('symbol', 'order_type', 'status')