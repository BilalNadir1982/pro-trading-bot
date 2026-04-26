import requests
import pandas as pd
from config import *
from strategy import calculate, signal


def send(msg):
    print("SEND:", msg)  # DEBUG

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

    print("TELEGRAM RESPONSE:", r.text)


def get_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 100}

    data = requests.get(url, params=params).json()

    if not isinstance(data, list):
        return None

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df


def run():

    print("BOT STARTED")

    # 🔥 TELEGRAM TEST (EN ÖNEMLİ)
    send("🚀 BOT AKTİF - TEST MESAJI")

    for symbol in SYMBOLS:

        print("CHECK:", symbol)

        df = get_data(symbol)
        if df is None:
            continue

        df = calculate(df)

        sig, tp, sl = signal(df)

        print("SIGNAL:", symbol, sig)

        if sig:

            msg = f"""
🚀 SİNYAL

Coin: {symbol}
Tip: {sig}
Entry: {df.iloc[-1]['close']}

TP: {round(tp,2)}
SL: {round(sl,2)}
"""

            send(msg)


run()
