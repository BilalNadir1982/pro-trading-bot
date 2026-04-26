import requests
import pandas as pd
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
        print("Telegram error")


# =========================
# COINGECKO DATA (FIXED)
# =========================
def get_data(symbol):

    try:
        coin = COINS.get(symbol)

        if not coin:
            print(symbol, "NO MAP")
            return None

        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"

        params = {
            "vs_currency": "usd",
            "days": 1,
            "interval": "hourly"
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            print(symbol, "API ERROR")
            return None

        data = r.json()

        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])

        if not prices or not volumes:
            print(symbol, "EMPTY DATA")
            return None

        df = pd.DataFrame(prices, columns=["time", "close"])
        df["volume"] = [v[1] for v in volumes]

        return df

    except Exception as e:
        print(symbol, "ERROR", e)
        return None


# =========================
# INDICATORS
# =========================
def prepare(df):

    df["ema20"] = df["close"].rolling(5).mean()
    df["ema50"] = df["close"].rolling(10).mean()
    df["vol_ma"] = df["volume"].rolling(5).mean()

    return df


# =========================
# FILTER
# =========================
def smart_filter(df):

    last = df.iloc[-1]

    return last["volume"] > last["vol_ma"] * 1.2


# =========================
# SIGNAL ENGINE
# =========================
def signal(df):

    last = df.iloc[-1]

    if last["ema20"] > last["ema50"]:
        return "LONG"

    if last["ema20"] < last["ema50"]:
        return "SHORT"

    return None


# =========================
# MAIN LOOP
# =========================
def run():

    send("🚀 CLEAN COINGECKO BOT STARTED")

    for symbol in SYMBOLS:

        print("CHECK:", symbol)

        df = get_data(symbol)

        if df is None:
            send(f"{symbol} NO DATA")
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
Direction: {sig}
Price: {price}
""")

    send("✅ SCAN COMPLETE")


run()
