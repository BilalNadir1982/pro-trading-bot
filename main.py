import requests
import pandas as pd

from config import *
from strategy import calculate, spot_signal
from backtest import backtest
from optimize import optimize_params


# =========================
# TELEGRAM
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        print("Telegram error")


# =========================
# BINANCE DATA
# =========================
def get_data(symbol):

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 200}

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
# WHALE DETECTION
# =========================
def whale(df):

    try:
        avg = df["volume"].rolling(20).mean().iloc[-1]
        last = df["volume"].iloc[-1]
        return last > avg * 2
    except:
        return False


# =========================
# MAIN ENGINE
# =========================
def run():

    print("BOT STARTED")

    send("🚀 PRO AI BOT STARTED")

    # =====================
    # AI OPTIMIZATION
    # =====================
    best = optimize_params()
    send(f"🧠 OPTIMUM RSI LEVEL: {best['rsi']}")

    # =====================
    # BACKTEST (BTC SAMPLE)
    # =====================
    btc = get_data("BTCUSDT")

    if btc is not None:

        result = backtest(btc)

        send(f"""
📊 BACKTEST RESULT

Trades: {result['trades']}
Wins: {result['wins']}
Losses: {result['losses']}
Winrate: %{result['winrate']}
""")

    # =====================
    # TOP MOVERS
    # =====================
    movers = top_movers()

    if movers:
        send("🔥 TOP MOVERS:\n" +
             "\n".join([f"{x['symbol']} %{x['priceChangePercent']}" for x in movers]))

    # =====================
    # SCAN COINS
    # =====================
    for symbol in SYMBOLS:

        df = get_data(symbol)
        if df is None:
            continue

        df = calculate(df)

        price = df.iloc[-1]["close"]

        sig, tp, sl = spot_signal(df)

        if sig:

            send(f"""
🚀 SIGNAL

Coin: {symbol}
Type: {sig}
Price: {price}

TP: {tp}
SL: {sl}
""")

        if whale(df):

            send(f"""
🐋 WHALE ALERT

{symbol}
Volume Spike
Price: {price}
""")

    send("✅ SCAN COMPLETE")


run()
