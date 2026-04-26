print("BOT STARTED")
import requests
import pandas as pd
import time
from config import *
from strategy import calculate, signal

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 200}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df

def run():
    sent = {}

    while True:
        try:
            for symbol in SYMBOLS:

                df = get_data(symbol)
                df = calculate(df)

                sig, tp, sl = signal(df)

                if sig:
                    key = f"{symbol}_{sig}"

                    if key not in sent:
                        price = df.iloc[-1]["close"]

                        msg = f"""
🚀 SİNYAL

Coin: {symbol}
Tip: {sig}
Entry: {price}

TP: {round(tp,2)}
SL: {round(sl,2)}
"""
                        send(msg)
                        sent[key] = True

            time.sleep(60)

        except Exception as e:
            print(e)
            time.sleep(10)

run()
