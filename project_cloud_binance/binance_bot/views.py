from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
from .trading_bot import get_account_info

@csrf_exempt
def trade_coin(request):
    if request.method == 'GET':
        coin_code = request.GET.get('coin', 'BTC')
        order_type = request.GET.get('order_type', 'BUY')
        try:
            quantity = float(request.GET.get('quantity', 0.001))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Valor inválido para quantity.'}, status=400)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Corpo JSON inválido.'}, status=400)
        coin_code = data.get('coin', 'BTC')
        order_type = data.get('order_type', 'BUY')
        try:
            quantity = float(data.get('quantity', 0.001))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Valor inválido para quantity.'}, status=400)
    else:
        return JsonResponse({'error': 'Método não permitido. Use GET ou POST.'}, status=405)

    try:
        order = execute_trade(coin_code, order_type, quantity)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    response_data = {
        'symbol': order.symbol,
        'order_type': order.order_type,
        'price': str(order.price),
        'quantity': str(order.quantity),
        'status': order.status,
        'created_at': order.created_at.isoformat(),
    }
    return JsonResponse(response_data)

def account_info_view(request):
    try:
        account_info = get_account_info()  
        return JsonResponse(account_info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
