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
# STATE INIT (panel control)
# =========================
STATE = {
    "enabled": True,
    "mode": "safe"
}


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
# TELEGRAM PANEL COMMANDS
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
# LISTENER
# =========================
def listen():

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    try:
        r = requests.get(url, timeout=10).json()

        for i in r.get("result", []):

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
