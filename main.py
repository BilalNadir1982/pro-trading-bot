import requests
import pandas as pd
import time

# =========================
# TELEGRAM
# =========================
TOKEN = "BOT_TOKEN"
CHAT_ID = "CHAT_ID"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# COINS
# =========================
COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT"]


# =========================
# DATA
# =========================
def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","_","_","_","_","_","_"
    ])

    df["h"] = df["h"].astype(float)
    df["l"] = df["l"].astype(float)
    df["c"] = df["c"].astype(float)
    df["v"] = df["v"].astype(float)

    return df


def get_funding(symbol):
    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
    return requests.get(url).json()


def get_oi(symbol):
    url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
    return requests.get(url).json()


# =========================
# LIQUIDITY ENGINE
# =========================
def liquidity(df):
    sweep_up = df["h"].iloc[-1] > df["h"].iloc[-5:-1].max()
    sweep_down = df["l"].iloc[-1] < df["l"].iloc[-5:-1].min()
    return sweep_up, sweep_down


# =========================
# STRUCTURE ENGINE (BOS / CHOCH)
# =========================
def structure(df):
    bos = df["h"].iloc[-1] > df["h"].iloc[-3] and df["l"].iloc[-1] > df["l"].iloc[-3]
    choch = df["h"].iloc[-1] < df["h"].iloc[-3] and df["l"].iloc[-1] < df["l"].iloc[-3]
    return bos, choch


# =========================
# WHALE + CROWD
# =========================
def whale(symbol):
    fund = get_funding(symbol)
    oi = get_oi(symbol)

    fr = float(fund["lastFundingRate"])
    oi_v = float(oi["openInterest"])

    bias = 0

    if fr > 0.01:
        bias -= 1
    if fr < -0.01:
        bias += 1
    if oi_v > 0:
        bias += 0.5

    return bias


# =========================
# SCORE ENGINE
# =========================
def score(liq, smc, whale_bias):
    s = 0

    if liq[0]:
        s += 25
    if liq[1]:
        s -= 25

    if smc[0]:
        s += 30
    if smc[1]:
        s -= 30

    s += whale_bias * 20

    return s


# =========================
# MAIN
# =========================
def run(symbol):
    df = get_klines(symbol)

    liq = liquidity(df)
    smc = structure(df)
    w = whale(symbol)

    sc = score(liq, smc, w)

    if sc > 40:
        signal = "🟢 BUY"
    elif sc < -40:
        signal = "🔴 SELL"
    else:
        return

    msg = f"""
🧠 PRO SIGNAL ENGINE V3

Coin: {symbol}
Signal: {signal}
Score: {sc}

📊 Liquidity Sweep: {liq}
🧠 Structure (BOS/CHoCH): {smc}
🐋 Whale Bias: {w}
"""

    send(msg)


# =========================
# LOOP
# =========================
while True:
    for c in COINS:
        try:
            run(c)
            time.sleep(1)
        except:
            pass

    time.sleep(60)
