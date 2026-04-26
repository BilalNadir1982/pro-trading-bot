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
        r = requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
        print("TG:", r.text)
    except Exception as e:
        print("Telegram error:", e)


# =========================
# BINANCE DATA
# =========================
def get_data(symbol):

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 100}

    try:
        data = requests.get(url, params=params, timeout=10).json()
    except:
        return None

    if not isinstance(data, list):
        return None

    try:
        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
        df.columns = ["time","open","high","low","close","volume"]

        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df

    except:
        return None


# =========================
# TOP MOVERS (FIXED)
# =========================
def top_movers():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:
        data = requests.get(url, timeout=10).json()
    except:
        return []

    if not isinstance(data, list):
        return []

    cleaned = []

    for x in data:

        if not isinstance(x, dict):
            continue

        try:
            change = float(x.get("priceChangePercent", 0))
            x["priceChangePercent"] = change
            cleaned.append(x)
        except:
            continue

    sorted_data = sorted(
        cleaned,
        key=lambda x: x["priceChangePercent"],
        reverse=True
    )

    return sorted_data[:5]


# =========================
# WHALE DETECTION
# =========================
def volume_spike(df):

    try:
        avg = df["volume"].rolling(20).mean().iloc[-1]
        last = df["volume"].iloc[-1]

        return last > avg * 2
    except:
        return False


# =========================
# BOT CORE
# =========================
def run():

    print("BOT STARTED")

    # 🔥 TEST MESAJI
    send("🚀 BOT AKTİF")

    movers = top_movers()

    if movers:
        msg = "🔥 TOP MOVERS:\n"
        for m in movers:
            msg += f"{m['symbol']} % {m['priceChangePercent']}\n"
        send(msg)

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            continue

        df = calculate(df)

        price = df.iloc[-1]["close"]

        # ================= SPOT
        sig, tp, sl = spot_signal(df)

        if sig:
            send(f"""
🚀 SPOT SIGNAL

Coin: {symbol}
Type: {sig}
Price: {price}

TP: {round(tp,2)}
SL: {round(sl,2)}
""")

        # ================= FUTURES
        fut = futures_signal(df)

        if fut:
            send(f"""
⚡ FUTURES SIGNAL

Coin: {symbol}
Direction: {fut}
Price: {price}
""")

        # ================= WHALE
        if volume_spike(df):
            send(f"""
🐋 WHALE ALERT

Coin: {symbol}
Volume Spike
Price: {price}
""")


# =========================
# START
# =========================
run()
