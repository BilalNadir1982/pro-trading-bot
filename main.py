import requests
import pandas as pd
from config import *

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
    except:
        print("Telegram error")


# =========================
# DATA (BINANCE FUTURES)
# =========================
def get_data(symbol):

    url = "https://fapi.binance.com/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 100
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            print(symbol, "HTTP ERROR", r.status_code)
            return None

        data = r.json()

        if not isinstance(data, list):
            print(symbol, "NO DATA")
            return None

        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
        df.columns = ["time","open","high","low","close","volume"]

        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df

    except Exception as e:
        print(symbol, "ERROR", e)
        return None


# =========================
# INDICATORS
# =========================
def prepare(df):

    df["ema20"] = df["close"].rolling(20).mean()
    df["ema50"] = df["close"].rolling(50).mean()

    df["vol_ma"] = df["volume"].rolling(20).mean()

    return df


# =========================
# SMART FILTER
# =========================
def smart_filter(df):

    last = df.iloc[-1]

    if last["volume"] > last["vol_ma"] * 1.2:
        return True

    return False


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

    send("🚀 PRO TRADING BOT STARTED")

    for symbol in SYMBOLS:

        print("CHECK:", symbol)

        df = get_data(symbol)

        if df is None:
            send(f"{symbol} DATA FAILED")
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
