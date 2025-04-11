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

# Carrega as variáveis de ambiente (mantém o que for necessário)
load_dotenv()
BASE_URL = "https://testnet.binance.vision"
API_KEY = os.getenv("BINANCE_API_KEY")

# =======================
# AQUI FOI AJUSTADO:
# Em vez de usar uma variável de ambiente com caminho absoluto, carregamos a chave privada
# a partir de um arquivo utilizando caminhos relativos.
# =======================

# Obtém o diretório deste arquivo (trading_bot.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível para chegar à pasta 'binance_bot'
project_binance_bot_dir = os.path.dirname(current_dir)
# Sobe outro nível para chegar à pasta 'project_cloud_binance'
project_dir = os.path.dirname(project_binance_bot_dir)
# Sobe mais um nível para atingir a raiz do repositório, supondo que a pasta secrets esteja lá
root_dir = os.path.dirname(project_dir)
# Monta o caminho relativo para o arquivo da chave privada
private_key_file = os.path.join(root_dir, "secrets", "test-prv-key.pem")

# Lê o conteúdo do arquivo da chave privada
with open(private_key_file, "rb") as key_file:
    PRIVATE_KEY_PEM = key_file.read().decode("utf-8")

# Carrega a chave privada utilizando a biblioteca cryptography
private_key = serialization.load_pem_private_key(
    PRIVATE_KEY_PEM.encode(), password=None, backend=default_backend()
)

# =======================
# O restante do código permanece igual
# =======================

def generate_signature(params, private_key):
    query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    signature = private_key.sign(query_string.encode('ascii'))
    return base64.b64encode(signature).decode('utf-8')

def execute_trade(coin_code, order_type, quantity):
    coin_code = coin_code.upper()
    symbol = coin_code if coin_code.endswith("USDT") else coin_code + "USDT"

    ticker_url = f'{BASE_URL}/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(ticker_url)
    response.raise_for_status()
    price = float(response.json()['price'])
    valid_price = round(price * 0.99, 2) if order_type.upper() == 'BUY' else round(price * 1.01, 2)

    params = {
        'symbol': symbol,
        'side': order_type.upper(),
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': str(quantity),
        'price': str(valid_price),
        'timestamp': int(time.time() * 1000)
    }

    signature = generate_signature(params, private_key)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': API_KEY}

    trade_url = 'https://testnet.binance.vision/api/v3/order'
    response = requests.post(trade_url, headers=headers, data=params)
    order_data = response.json()

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
    response.raise_for_status()
    return response.json()
