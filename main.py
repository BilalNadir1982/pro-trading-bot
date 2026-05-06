import os
from binance.client import Client
import requests
import time

API_KEY = os.getenv("kudx5MdcG0vtL6ROzXFUDfk1EiLr48ocu1hVRre8xCvFee1ZTcUcfAssE9OADm8y")
API_SECRET = os.getenv("oD96EwztNLMOoMl6sM5HbutHADS14kT8kY5SniupXecquNz6rkkpdFaOrk6PzdGY")

BOT_TOKEN = os.getenv("8515071054:AAG0tMwV6RH_rzMHkXrkECmP6UyOJekXXZo")
CHAT_ID = os.getenv("768262682")

client = Client(API_KEY, API_SECRET)

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])

while True:
    price = get_price("BTCUSDT")

    send(f"📊 BTC Price: {price}")

    time.sleep(60)
