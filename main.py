import requests
import pandas as pd
import time
import ta
from config import BOT_TOKEN, CHAT_ID, MIN_SCORE

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

# =========================
# FIXED REQUEST (IMPORTANT)
# =========================
def safe_get(url, params=None):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        try:
            return r.json()
        except:
            return None

    except:
        return None

# =========================
# COINS
# =========================
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]

# =========================
# DATA
# =========================
def get_data(symbol):

    url = "https://api.binance.com/api/v3/klines"

    r = safe_get(url, {
        "symbol": symbol,
        "interval": "15m",
        "limit": 100
    })

    if not r or not isinstance(r, list):
        return None

    df = pd.DataFrame(r, columns=[
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
    df["signal"] = macd.macd_signal()

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

    return max(0, min(100, s))

# =========================
# RUN
# =========================
def run():

    send("🚀 FIXED BOT STARTED")

    for symbol in COINS:

        df = get_data(symbol)

        if df is None:
            send(f"❌ STILL FAIL: {symbol}")
            continue

        df = indicators(df)

        last = df.iloc[-1]
        sc = score(last)

        send(f"📊 {symbol} SCORE: {sc}")

        if sc >= MIN_SCORE:

            direction = "LONG" if last["macd"] > last["signal"] else "SHORT"

            send(f"""
🔥 SIGNAL

Coin: {symbol}
Score: {sc}
Direction: {direction}
""")

        time.sleep(1)

if __name__ == "__main__":
    run()
