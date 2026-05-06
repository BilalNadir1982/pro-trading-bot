import requests
import pandas as pd
import time
import ta

from config import BOT_TOKEN, CHAT_ID, MIN_SCORE

# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# COIN LIST (CoinGecko)
# =========================
def get_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    data = requests.get(url, params=params).json()
    return [c["symbol"].upper() + "USDT" for c in data]

# =========================
# BINANCE PUBLIC DATA
# =========================
def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "15m",
        "limit": 100
    }

    r = requests.get(url, params=params).json()

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

    df["adx"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()

    atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"])
    df["atr"] = atr.average_true_range()

    return df

# =========================
# SCORE ENGINE (PRO MAX)
# =========================
def score(row):
    s = 50

    # RSI
    if row["rsi"] < 30:
        s += 15
    elif row["rsi"] > 70:
        s -= 15

    # MACD
    if row["macd"] > row["signal"]:
        s += 20
    else:
        s -= 20

    # ADX trend strength
    if row["adx"] > 25:
        s += 10

    return max(0, min(100, s))

# =========================
# MAIN LOOP
# =========================
def run():
    coins = get_coins()

    send("🚀 PRO MAX BOT STARTED")

    for symbol in coins:
        try:
            df = get_data(symbol)
            df = indicators(df)

            last = df.iloc[-1]
            sc = score(last)

            if sc >= MIN_SCORE:

                direction = "LONG" if last["macd"] > last["signal"] else "SHORT"

                msg = f"""
🔥 PRO SIGNAL

📌 Coin: {symbol}
📊 Score: {sc}
📈 Direction: {direction}

RSI: {last['rsi']:.2f}
ADX: {last['adx']:.2f}
ATR: {last['atr']:.2f}
"""

                send(msg)

            time.sleep(0.2)  # API limit koruması

        except:
            continue

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
