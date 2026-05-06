from modules.scanner import get_top_symbols
from modules.indicators import add_indicators
from modules.scorer import score_row
from modules.telegram import send
from modules.filters import allow
from binance.client import Client
import pandas as pd

client = Client()

def get_data(symbol):
    klines = client.get_klines(symbol=symbol, interval="15m", limit=100)
    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "c1","c2","c3","c4","c5","c6"
    ])

    df = df.astype(float)
    return df

while True:
    symbols = get_top_symbols()

    for symbol in symbols:
        try:
            df = get_data(symbol)
            df = add_indicators(df)

            last = df.iloc[-1]
            score = score_row(last)

            if score >= 75 and allow(symbol):
                direction = "LONG" if last["macd"] > last["macd_signal"] else "SHORT"

                msg = f"""
🔥 STRONG SIGNAL
{symbol}

📊 Score: {score}
📈 Direction: {direction}
RSI: {last['rsi']:.2f}
ADX: {last['adx']:.2f}
"""

                send(msg)

        except:
            continue
