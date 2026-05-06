import os
import time
import pandas as pd
import requests
from binance.client import Client
import ta

# =========================
# ENV CONFIG (GitHub Secrets)
# =========================
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Client(API_KEY, API_SECRET)

# =========================
# SPAM CONTROL
# =========================
last_signal_time = {}

COOLDOWN = 900  # 15 dakika
MIN_SCORE = 75

# =========================
# TELEGRAM SEND
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# COIN LIST (TOP 100 USDT)
# =========================
def get_symbols():
    tickers = client.get_ticker()
    symbols = [t["symbol"] for t in tickers if t["symbol"].endswith("USDT")]
    return symbols[:100]

# =========================
# PRICE DATA
# =========================
def get_data(symbol):
    klines = client.get_klines(symbol=symbol, interval="15m", limit=100)

    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "c1","c2","c3","c4","c5","c6"
    ])

    df = df[["open","high","low","close","volume"]].astype(float)
    return df

# =========================
# INDICATORS
# =========================
def indicators(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df["adx"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()

    atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"])
    df["atr"] = atr.average_true_range()

    return df

# =========================
# SCORE ENGINE
# =========================
def score(row):
    s = 50

    # RSI
    if row["rsi"] < 30:
        s += 15
    elif row["rsi"] > 70:
        s -= 15

    # MACD
    if row["macd"] > row["macd_signal"]:
        s += 20
    else:
        s -= 20

    # ADX trend strength
    if row["adx"] > 25:
        s += 10

    return max(0, min(100, s))

# =========================
# SPAM FILTER
# =========================
def allow(symbol):
    now = time.time()

    if symbol in last_signal_time:
        if now - last_signal_time[symbol] < COOLDOWN:
            return False

    last_signal_time[symbol] = now
    return True

# =========================
# MAIN LOOP
# =========================
def run():
    symbols = get_symbols()

    for symbol in symbols:
        try:
            df = get_data(symbol)
            df = indicators(df)

            last = df.iloc[-1]
            sc = score(last)

            if sc >= MIN_SCORE and allow(symbol):

                direction = "LONG" if last["macd"] > last["macd_signal"] else "SHORT"

                msg = f"""
🔥 STRONG SIGNAL

📌 Coin: {symbol}
📊 Score: {sc}
📈 Direction: {direction}

RSI: {last['rsi']:.2f}
ADX: {last['adx']:.2f}
ATR: {last['atr']:.2f}
"""

                send(msg)

        except Exception as e:
            continue

# =========================
# START
# =========================
if __name__ == "__main__":
    send("🚀 BOT STARTED")  # 👈 BURAYA EKLİYORSUN
    run()
