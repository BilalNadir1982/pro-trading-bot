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
# DATA
# =========================
def get_data(symbol):

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 100
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
        df.columns = ["time","open","high","low","close","volume"]

        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df

    except:
        return None


# =========================
# PREP
# =========================
def prepare(df):

    df["ema20"] = df["close"].rolling(20).mean()
    df["ema50"] = df["close"].rolling(50).mean()

    return df


# =========================
# FILTER (SMART MONEY)
# =========================
def smart_filter(df):

    vol = df["volume"].iloc[-1]
    avg = df["volume"].rolling(20).mean().iloc[-1]

    return vol > avg * 1.2


# =========================
# SIGNAL
# =========================
def signal(df):

    last = df.iloc[-1]

    if last["ema20"] > last["ema50"]:
        return "BUY"

    if last["ema20"] < last["ema50"]:
        return "SELL"

    return None


# =========================
# WINRATE (BASİT)
# =========================
stats = {"win":0, "loss":0}

def winrate():

    total = stats["win"] + stats["loss"]

    if total == 0:
        return 0

    return stats["win"] / total * 100


# =========================
# MAIN LOOP
# =========================
def run():

    send("🚀 FINAL BOT STARTED")

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            send(f"{symbol} DATA ERROR")
            continue

        df = prepare(df)

        if not smart_filter(df):
            continue

        sig = signal(df)

        if sig:

            price = df.iloc[-1]["close"]

            send(f"""
🚨 SIGNAL

Coin: {symbol}
Signal: {sig}
Price: {price}

Winrate: {winrate():.2f}%
""")

    send("✅ SCAN COMPLETE")


run()
