import json
import requests
import time
import os
import base64
from dotenv import load_dotenv
from django.http import JsonResponse
from .models import TradeOrder

# Imports to use the private key for signing
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Load environment variables
load_dotenv()
API_KEY ='EmdjuaXJejDC7bWwdvzlefNXzCbhADwogNBWFNyiZilMWEQ7y8yyhrWAqc1PFeyP'
# You can set PRIVATE_KEY_PATH in your .env; otherwise it defaults to 'test-prv-key.pem'
PRIVATE_KEY_PATH ='../test-prv-key.pem'

# Load the private key from the PEM file
with open(PRIVATE_KEY_PATH, 'rb') as key_file:
    private_key = load_pem_private_key(key_file.read(), password=None)

BASE_URL = "https://api.binance.com"  # Base URL for Binance API

def generate_signature(params, private_key):
    """
    Generate a signature by signing the query string payload using the private key.
    The parameters are first sorted and concatenated in the format key=value.
    The signature is returned as a base64-encoded string.
    """
    # Concatenate sorted parameters into a query string
    query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    signature = private_key.sign(query_string.encode('ascii'))
    return base64.b64encode(signature).decode('utf-8')

def execute_trade(coin_code, order_type, quantity):
    """
    Executes a trade order using the Binance Testnet API.

    - If the provided coin code does not end with 'USDT', the code appends it.
    - For BUY orders, the trade price is set to 1% below the current market price;
      for SELL orders, the price is set to 1% above.
    - The request payload is signed using the loaded private key.
    """
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

    # Set the headers with your API key
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
    """
    API endpoint to execute a trade operation.

    Supported methods:
      - GET: parameters passed via the query string.
      - POST: parameters passed in the JSON body.

    Expected parameters:
      - coin: coin code (e.g., BTC, ETH). 'USDT' is appended automatically if missing.
      - order_type: either "BUY" or "SELL".
      - quantity: the amount to trade.
    """
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
