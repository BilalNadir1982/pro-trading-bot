import requests
import pandas as pd
from config import *
from strategy import calculate, spot_signal, futures_signal


# =========================
# TELEGRAM
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram error")


# =========================
# BINANCE DATA
# =========================
def get_data(symbol):

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 100}

    try:
        data = requests.get(url, params=params).json()
    except:
        return None

    if not isinstance(data, list):
        return None

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df


# =========================
# WHALE / VOLUME SPIKE
# =========================
def volume_spike(df):

    avg = df["volume"].rolling(20).mean().iloc[-1]
    last = df["volume"].iloc[-1]

    return last > avg * 2


# =========================
# TOP MOVERS
# =========================
def top_movers():

    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = requests.get(url).json()

    sorted_data = sorted(
        data,
        key=lambda x: float(x["priceChangePercent"]),
        reverse=True
    )

    return sorted_data[:5]


# =========================
# BOT CORE
# =========================
def run():

    print("BOT STARTED")

    send("🚀 PRO BOT AKTİF")

    # TOP COINS INFO
    movers = top_movers()
    send("🔥 TOP MOVERS:\n" + "\n".join([x["symbol"] for x in movers[:5]]))

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            continue

        df = calculate(df)

        # ================= SPOT
        sig, tp, sl = spot_signal(df)

        # ================= FUTURES
        fut = futures_signal(df)

        # ================= WHALE CHECK
        whale = volume_spike(df)

        price = df.iloc[-1]["close"]

        # ================= MESSAGE
        if sig:

            msg = f"""
🚀 SPOT SIGNAL

Coin: {symbol}
Type: {sig}
Price: {price}

TP: {round(tp,2)}
SL: {round(sl,2)}
"""

            send(msg)

        if fut:

            send(f"""
⚡ FUTURES SIGNAL

Coin: {symbol}
Direction: {fut}
Price: {price}
""")

        if whale:

            send(f"""
🐋 WHALE ALERT

Coin: {symbol}
Volume Spike Detected!
Price: {price}
""")

    send("✅ SCAN COMPLETE")


run()
