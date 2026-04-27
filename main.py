import requests
import pandas as pd
import time
from config import *

# =========================
# TELEGRAM SEND
# =========================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        print("Telegram error")


# =========================
# STATE
# =========================
STATE = {
    "enabled": True,
    "mode": "safe"
}

LAST_UPDATE_ID = None
LAST_SIGNALS = {}


# =========================
# BINANCE DATA
# =========================
def get_data(symbol):

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

        return df

    except:
        return None


# =========================
# SIGNAL ENGINE
# =========================
def signal(df):

    ema20 = df["c"].rolling(5).mean()
    ema50 = df["c"].rolling(10).mean()

    if ema20.iloc[-1] > ema50.iloc[-1]:
        return "LONG"

    if ema20.iloc[-1] < ema50.iloc[-1]:
        return "SHORT"

    return None


# =========================
# TELEGRAM COMMANDS
# =========================
def handle(text):

    if text == "/on":
        STATE["enabled"] = True
        send("✅ BOT ON")

    elif text == "/off":
        STATE["enabled"] = False
        send("⛔ BOT OFF")

    elif text == "/status":
        send(f"""
📊 BOT STATUS

Enabled: {STATE['enabled']}
Mode: {STATE['mode']}
""")


# =========================
# LISTENER (FIXED)
# =========================
def listen():
    global LAST_UPDATE_ID

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    try:
        params = {}

        if LAST_UPDATE_ID:
            params["offset"] = LAST_UPDATE_ID + 1

        r = requests.get(url, params=params, timeout=10).json()

        for i in r.get("result", []):

            LAST_UPDATE_ID = i["update_id"]

            try:
                text = i["message"]["text"]
                handle(text)
            except:
                pass

    except:
        pass


# =========================
# MAIN ENGINE
# =========================
def run():

    if not STATE["enabled"]:
        return

    for symbol in SYMBOLS:

        df = get_data(symbol)

        if df is None:
            continue

        sig = signal(df)

        if sig:

            price = df["c"].iloc[-1]

            # aynı sinyal tekrarını engelle
            if LAST_SIGNALS.get(symbol) == sig:
                continue

            LAST_SIGNALS[symbol] = sig

            send(f"""
🚨 SIGNAL

Coin: {symbol}
Direction: {sig}
Price: {price}
""")


# =========================
# START
# =========================
send("🚀 BOT STARTED")

while True:

    listen()
    run()

    time.sleep(60)
