from django.urls import path
from django.http import HttpResponse
from .trading_bot import trade_coin  # Import the trade_coin function
from binance_bot import views  # Import the views module

def home(request):
    return HttpResponse("🤖 Trading bot na escuta!")

urlpatterns = [
    path('', home, name='home'),
    path('api/trade/', trade_coin, name='trade_coin'),
    path('account-info/', views.account_info_view, name='account_info'),
    path('coin-price/<str:coin>/', views.coin_price_view, name='coin_price'),
    path('order-history/', views.get_order_history, name='order_history'),
]
