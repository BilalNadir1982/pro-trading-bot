from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_top_symbols():
    tickers = client.get_ticker()
    usdt_pairs = [t["symbol"] for t in tickers if "USDT" in t["symbol"]]
    return usdt_pairs[:100]
