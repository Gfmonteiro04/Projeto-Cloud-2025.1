from django.urls import path
from django.http import HttpResponse
from .trading_bot import trade_coin
from . import views

def home(request):
    #api_key = os.getenv("BINANCE_API_KEY")
    return HttpResponse("🤖 Trading bot na escuta!") #(f"Trading bot na escuta! API Key: {api_key}")

urlpatterns = [
    path('', home, name='home'),
    path('api/trade/', trade_coin, name='trade_coin'),
    path('account-info/', views.account_info_view, name='account_info'),
]
