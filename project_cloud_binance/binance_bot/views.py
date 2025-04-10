from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import requests
import time
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

def coin_price_view(request, coin):
    try:
        # URL da API da Binance para obter a cotação
        url = f'https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT'

        # Faz a requisição GET para obter o preço
        response = requests.get(url)

        # Se a resposta for bem-sucedida
        if response.status_code == 200:
            data = response.json()
            price = data['price']  # Preço da moeda em USDT

            # Pega o timestamp atual
            timestamp = int(time.time() * 1000)  # Timestamp em milissegundos

            return JsonResponse({
                'coin': coin,
                'price': price,
                'timestamp': timestamp  # Retorna o timestamp do momento
            })
        else:
            return JsonResponse({'error': 'Moeda não encontrada ou erro ao consultar a API'}, status=400)

    except Exception as e:
        # Se ocorrer algum erro
        return JsonResponse({'error': str(e)}, status=500)

def get_order_history(request):
    coin_code = request.GET.get('coin', 'BTC')

    try:
        # Normaliza o símbolo da moeda
        coin_code = coin_code.upper()
        symbol = coin_code if coin_code.endswith("USDT") else coin_code + "USDT"

        endpoint = "/api/v3/allOrders"
        timestamp = int(time.time() * 1000)

        params = {
            "symbol": symbol,
            "timestamp": timestamp,
        }

        signature = generate_signature(params, private_key)
        params['signature'] = signature

        headers = {'X-MBX-APIKEY': API_KEY}
        url = BASE_URL + endpoint

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        orders = response.json()

        return JsonResponse({
            'symbol': symbol,
            'orders': orders
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
