import requests
import pandas as pd
import ta
from config import *


# =========================
# TELEGRAM
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass


# =========================
# DATA
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

    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df


# =========================
# INDICATORS
# =========================
def prepare(df):

    df["ema20"] = ta.trend.ema_indicator(df["close"], 20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)
    df["rsi"] = ta.momentum.rsi(df["close"], 14)

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    return df


# =========================
# AI FILTER
# =========================
def ai_filter(df):

    last = df.iloc[-1]

    score = 0

    if last["ema20"] > last["ema50"]:
        score += 1

    if 45 < last["rsi"] < 65:
        score += 1

    if last["macd"] > last["macd_signal"]:
        score += 1

    if df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1] * 1.5:
        score += 1

    return score >= 2


# =========================
# SMART MONEY
# =========================
def smart_money(df, symbol):

    vol = df["volume"].iloc[-1]
    avg = df["volume"].rolling(20).mean().iloc[-1]

    print(symbol, "VOL:", vol, "AVG:", avg)

    return vol > avg * 1.3

# =========================
# FUTURES ENGINE
# =========================
def futures(df):

    last = df.iloc[-1]

    if last["ema20"] > last["ema50"] and last["rsi"] < 50:
        return "LONG 5x"

    if last["ema20"] < last["ema50"] and last["rsi"] > 50:
        return "SHORT 5x"

    return None


# =========================
# TOP MOVERS
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
        try:
            x["priceChangePercent"] = float(x["priceChangePercent"])
            cleaned.append(x)
        except:
            continue

    return sorted(cleaned, key=lambda x: x["priceChangePercent"], reverse=True)[:5]


# =========================
# CORE AI ENGINE
# =========================
def run():

    send("🚀 AI PRO TRADING BOT STARTED")

    for symbol in SYMBOLS:

        df = get_data(symbol)
        if df is None:
            continue

        df = prepare(df)

        last = df.iloc[-1]
        price = last["close"]

        # DEBUG
        send(f"CHECK: {symbol}")

        ai_ok = ai_filter(df)
        smart_ok = smart_money(df, symbol)

        send(f"{symbol} AI:{ai_ok} SMART:{smart_ok}")

        lev = futures(df)

        # TEST MODU (KESİN SİNYAL GÖRMEK İÇİN)
        if True:

            send(f"""
🚀 TEST SIGNAL

Coin: {symbol}
Price: {price}

AI: {ai_ok}
SMART: {smart_ok}
Futures: {lev}
""")

    send("✅ SCAN COMPLETE")

run()
