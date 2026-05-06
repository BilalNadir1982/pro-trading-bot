import requests
import pandas as pd
import time
import ta
from config import BOT_TOKEN, CHAT_ID, MIN_SCORE

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =========================
# COINS
# =========================
def get_coins():
    return [
        "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
        "ADAUSDT","DOGEUSDT","AVAXUSDT","LINKUSDT","LTCUSDT",
        "DOTUSDT","TRXUSDT","MATICUSDT","ATOMUSDT","NEARUSDT",
        "UNIUSDT","APTUSDT","ICPUSDT","FILUSDT","OPUSDT",
        "ARBUSDT","SUIUSDT","INJUSDT","SEIUSDT","PEPEUSDT",
        "SHIBUSDT","WLDUSDT","BONKUSDT","FETUSDT","RNDRUSDT"
    ]

# =========================
# DATA
# =========================
def get_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": "15m", "limit": 100}

    try:
        r = requests.get(url, timeout=10).json()

        if not isinstance(r, list):
            return None

        df = pd.DataFrame(r, columns=[
            "time","open","high","low","close","volume",
            "c1","c2","c3","c4","c5","c6"
        ])

        df = df[["open","high","low","close","volume"]].astype(float)
        return df

    except:
        return None

# =========================
# INDICATORS
# =========================
def indicators(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    df["adx"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()

    return df

# =========================
# SCORE
# =========================
def score(row):
    s = 50

    if row["rsi"] < 30:
        s += 15
    elif row["rsi"] > 70:
        s -= 15

    if row["macd"] > row["signal"]:
        s += 20
    else:
        s -= 20

    if row["adx"] > 25:
        s += 10

    return max(0, min(100, s))

# =========================
# RUN
# =========================
def run():

    send("🚀 PRO MAX BOT STARTED")

    coins = get_coins()

    send(f"📊 Coins loaded: {len(coins)}")

    for symbol in coins:

        send(f"🔎 Checking: {symbol}")

        df = get_data(symbol)

        if df is None:
            send(f"❌ DATA ERROR: {symbol}")
            continue

        df = indicators(df)

        last = df.iloc[-1]
        sc = score(last)

        # 🔥 SCORE LOG (ÖNEMLİ)
        send(f"📊 {symbol} SCORE: {sc}")

        if sc >= MIN_SCORE:

            direction = "LONG" if last["macd"] > last["signal"] else "SHORT"

            send(f"""
🔥 PRO SIGNAL

📌 Coin: {symbol}
📊 Score: {sc}
📈 Direction: {direction}

RSI: {last['rsi']:.2f}
ADX: {last['adx']:.2f}
""")

        time.sleep(0.2)

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
