import json
import requests
import time
import os
import base64
from dotenv import load_dotenv
from django.http import JsonResponse
from .models import TradeOrder


from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


load_dotenv()
BASE_URL = "https://testnet.binance.vision"
API_KEY = os.getenv("BINANCE_API_KEY")
PRIVATE_KEY_PEM = os.getenv("PRIVATE_KEY")
private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM.encode(), password=None, backend=default_backend())

def generate_signature(params, private_key):
    query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    signature = private_key.sign(query_string.encode('ascii'))
    return base64.b64encode(signature).decode('utf-8')

def execute_trade(coin_code, order_type, quantity):
    # Normalize coin code and append 'USDT' if not provided
    coin_code = coin_code.upper()
    symbol = coin_code if coin_code.endswith("USDT") else coin_code + "USDT"

    # Get the current price from Binance
    ticker_url = f'{BASE_URL}/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(ticker_url)
    response.raise_for_status()  # Raise an error if request fails
    price = float(response.json()['price'])

    # Determine the valid price: 1% discount for BUY, 1% premium for SELL
    valid_price = round(price * 0.99, 2) if order_type.upper() == 'BUY' else round(price * 1.01, 2)

    # Prepare the parameters for the order
    params = {
        'symbol': symbol,
        'side': order_type.upper(),
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': str(quantity),
        'price': str(valid_price),
        'timestamp': int(time.time() * 1000)
    }

    # Generate the signature with the private key
    signature = generate_signature(params, private_key)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': API_KEY}

    # Binance Testnet order endpoint
    trade_url = 'https://testnet.binance.vision/api/v3/order'
    response = requests.post(trade_url, headers=headers, data=params)
    order_data = response.json()

    # Save the order details in the database
    order = TradeOrder.objects.create(
        symbol=symbol,
        order_type=order_type.upper(),
        price=valid_price,
        quantity=quantity,
        status=order_data.get('status', 'PENDING')
    )
    return order

def trade_coin(request):
    if request.method == 'GET':
        coin_code = request.GET.get('coin', 'BTC')
        order_type = request.GET.get('order_type', 'BUY')
        try:
            quantity = float(request.GET.get('quantity', 0.001))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid value for quantity.'}, status=400)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        coin_code = data.get('coin', 'BTC')
        order_type = data.get('order_type', 'BUY')
        try:
            quantity = float(data.get('quantity', 0.001))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid value for quantity.'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed. Use GET or POST.'}, status=405)

    try:
        order = execute_trade(coin_code, order_type, quantity)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Return the order details as JSON
    response_data = {
        'symbol': order.symbol,
        'order_type': order.order_type,
        'price': str(order.price),
        'quantity': str(order.quantity),
        'status': order.status,
        'created_at': order.created_at.isoformat(),
    }
    return JsonResponse(response_data)

def get_account_info():
    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = {
        "timestamp": timestamp
    }

    signature = generate_signature(params, private_key)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': API_KEY}

    url = BASE_URL + endpoint
    response = requests.get(url, headers=headers, data=params)
    # Verifica se a requisição foi bem-sucedida
    response.raise_for_status()
    return response.json()
