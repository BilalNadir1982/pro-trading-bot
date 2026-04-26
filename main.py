import requests
import pandas as pd
from config import *

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        print("telegram error")


# =========================
# BINANCE DATA (PRIMARY)
# =========================
def get_binance(symbol):

    try:
        url = "https://fapi.binance.com/fapi/v1/klines"

        params = {
            "symbol": symbol,
            "interval": "15m",
            "limit": 50
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
        df.columns = ["t","o","h","l","c","v"]

        df["c"] = df["c"].astype(float)
        df["v"] = df["v"].astype(float)

        return df

    except:
        return None


# =========================
# COINPAPRIKA (FALLBACK)
# =========================
def get_paprika(symbol):

    try:
        coin = symbol.replace("USDT","").lower()

        url = f"https://api.coinpaprika.com/v1/tickers/{coin}-{coin}"

        r = requests.get(url, timeout=10)
        data = r.json()

        if "quotes" not in data:
            return None

        price = data["quotes"]["USD"]["price"]
        volume = data["quotes"]["USD"]["volume_24h"]

        df = pd.DataFrame([{
            "c": price,
            "v": volume
        }])

        return df

    except:
        return None


# =========================
# HYBRID DATA ENGINE
# =========================
def get_data(symbol):

    df = get_binance(symbol)

    if df is not None:
        return df

    print(symbol, "BINANCE FAIL → PAPRIKA")

    return get_paprika(symbol)


# =========================
# INDICATORS
# =========================
def prepare(df):

    df["ema20"] = df["c"].rolling(5).mean()
    df["ema50"] = df["c"].rolling(10).mean()
    df["vol_ma"] = df["v"].rolling(5).mean()

    return df


# =========================
# FILTER
# =========================
def filter(df):

    last = df.iloc[-1]

    return last["v"] > last["vol_ma"] * 1.2


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
# MAIN
# =========================
def run():

    send("🚀 HYBRID BOT STARTED")

    for s in SYMBOLS:

        print("CHECK:", s)

        df = get_data(s)

        if df is None:
            send(f"{s} NO DATA")
            continue

        df = prepare(df)

        if not filter(df):
            continue

        sig = signal(df)

        if sig:

            price = df.iloc[-1]["c"]

            send(f"""
🚨 SIGNAL

Coin: {s}
Direction: {sig}
Price: {price}
""")

    send("✅ SCAN COMPLETE")


run()
