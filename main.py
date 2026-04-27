import requests
import pandas as pd
import time
from config import *

# =========================
# TELEGRAM
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
    "mode": "normal"  # safe / normal / aggressive
}

LAST_UPDATE_ID = None
LAST_SIGNALS = {}

# =========================
# DATA
# =========================
def get_data(symbol):
    try:
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {
            "symbol": symbol,
            "interval": "5m",
            "limit": 100
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
# RSI
# =========================
def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =========================
# SIGNAL ENGINE
# =========================
def signal(df):

    ema20 = df["c"].ewm(span=20).mean()
    ema50 = df["c"].ewm(span=50).mean()
    rsi_val = rsi(df["c"])

    volume = df["v"].iloc[-1]
    avg_vol = df["v"].rolling(20).mean().iloc[-1]

    # HACİM FİLTRESİ
    if volume < avg_vol:
        return None

    # MODE AYARI
    if STATE["mode"] == "safe":
        rsi_low, rsi_high = 25, 75
    elif STATE["mode"] == "aggressive":
        rsi_low, rsi_high = 40, 60
    else:
        rsi_low, rsi_high = 30, 70

    # LONG
    if ema20.iloc[-1] > ema50.iloc[-1] and rsi_val.iloc[-1] < rsi_low:
        return "LONG"

    # SHORT
    if ema20.iloc[-1] < ema50.iloc[-1] and rsi_val.iloc[-1] > rsi_high:
        return "SHORT"

    return None

# =========================
# TELEGRAM COMMAND
# =========================
def handle(text):

    if not text.startswith("/"):
        return

    if text == "/on":
        STATE["enabled"] = True
        send("✅ BOT ON")

    elif text == "/off":
        STATE["enabled"] = False
        send("⛔ BOT OFF")

    elif text == "/safe":
        STATE["mode"] = "safe"
        send("🛡 SAFE MODE")

    elif text == "/normal":
        STATE["mode"] = "normal"
        send("⚖️ NORMAL MODE")

    elif text == "/aggressive":
        STATE["mode"] = "aggressive"
        send("🔥 AGGRESSIVE MODE")

    elif text == "/status":
        send(f"""
📊 BOT STATUS

Enabled: {STATE['enabled']}
Mode: {STATE['mode']}
""")

# =========================
# LISTEN (FIXED)
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
# RUN
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

            # tekrar engelle
            if LAST_SIGNALS.get(symbol) == sig:
                continue

            LAST_SIGNALS[symbol] = sig

            price = df["c"].iloc[-1]

            send(f"""
🚨 FUTURES SIGNAL

Coin: {symbol}
Direction: {sig}
Price: {price}

Mode: {STATE['mode']}
""")

# =========================
# START
# =========================
send("🚀 PRO BOT STARTED")

while True:

    listen()
    run()

    time.sleep(60)
