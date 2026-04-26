import requests
import pandas as pd
import time

from config import *


# =========================
# TELEGRAM
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
    except:
        print("telegram error")


# =========================
# DATA FIX (STABLE)
# =========================
def get_data(symbol):

    urls = [
        "https://api.binance.com/api/v3/klines",
        "https://api1.binance.com/api/v3/klines"
    ]

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 100
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:

        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            if isinstance(data, list) and len(data) > 0:

                df = pd.DataFrame(data)
                df = df.iloc[:, :6]
                df.columns = ["time","open","high","low","close","volume"]

                df["close"] = df["close"].astype(float)
                df["volume"] = df["volume"].astype(float)

                return df

        except:
            continue

    return None


# =========================
# INDICATORS
# =========================
def prepare(df):

    df["ema20"] = df["close"].rolling(20).mean()
    df["ema50"] = df["close"].rolling(50).mean()

    return df


# =========================
# SMART FILTER
# =========================
def smart_money(df):

    vol = df["volume"].iloc[-1]
    avg = df["volume"].rolling(20).mean().iloc[-1]

    return vol > avg * 1.2


# =========================
# SIGNAL ENGINE
# =========================
def signal(df):

    last = df.iloc[-1]

    if last["ema20"] > last["ema50"]:
        return "BUY"

    if last["ema20"] < last["ema50"]:
        return "SELL"

    return None


# =========================
# TOP MOVERS
# =========================
def movers():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:
        data = requests.get(url, timeout=10).json()

        sorted_data = sorted(
            data,
            key=lambda x: float(x["priceChangePercent"]),
            reverse=True
        )

        return sorted_data[:5]

    except:
        return []


# =========================
# MAIN LOOP
# =========================
def run():

    send("🚀 SAFE PRO BOT STARTED")

    top = movers()

    if top:
        send("🔥 TOP MOVERS:\n" +
             "\n".join([f"{x['symbol']} %{x['priceChangePercent']}" for x in top]))

    for symbol in SYMBOLS:

        send(f"CHECK: {symbol}")

        df = get_data(symbol)

        if df is None:
            send(f"{symbol} DATA FAILED")
            continue

        df = prepare(df)

        if not smart_money(df):
            continue

        sig = signal(df)

        if sig:

            price = df.iloc[-1]["close"]

            send(f"""
🚨 SAFE SIGNAL

Coin: {symbol}
Signal: {sig}
Price: {price}
""")


    send("✅ SCAN COMPLETE")


run()
