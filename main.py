import requests
from config import BOT_TOKEN, CHAT_ID

# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram error")

# =========================
# DATA
# =========================
def get_tickers():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        return requests.get(url, timeout=10).json()
    except:
        return []

def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        data = requests.get(url, timeout=10).json()
        return [float(x[4]) for x in data]
    except:
        return []

# =========================
# EMA
# =========================
def ema(data, period):
    k = 2 / (period + 1)
    val = data[0]
    for price in data:
        val = price * k + val * (1 - k)
    return val

# =========================
# SCORE
# =========================
def score(change, volume):
    s = 0
    if change > 5: s += 20
    elif change > 2: s += 10
    if change < -5: s -= 20
    elif change < -2: s -= 10

    if volume > 1_000_000_000: s += 20
    elif volume > 500_000_000: s += 10

    return s

# =========================
# ANALYZE
# =========================
def analyze(symbol):
    closes = get_klines(symbol)
    if len(closes) < 50:
        return None

    ema20 = ema(closes[-20:], 20)
    ema50 = ema(closes[-50:], 50)
    price = closes[-1]

    if ema20 > ema50 and price > ema20:
        return "UP"
    elif ema20 < ema50 and price < ema20:
        return "DOWN"
    return "SIDE"

# =========================
# SIGNAL
# =========================
def get_signal():
    data = get_tickers()
    best = None
    best_score = -999

    for d in data:
        symbol = d["symbol"]
        if "USDT" not in symbol:
            continue

        change = float(d["priceChangePercent"])
        volume = float(d["quoteVolume"])
        price = float(d["lastPrice"])

        trend = analyze(symbol)
        if not trend:
            continue

        sc = score(change, volume)

        if trend == "UP":
            sc += 20
        elif trend == "DOWN":
            sc -= 20

        if sc > best_score:
            best_score = sc
            best = (symbol, price, sc, trend)

    if not best:
        return "NO DATA"

    s, p, sc, t = best

    if sc > 50 and t == "UP":
        return f"🔥 STRONG BUY\n{s}\nPrice: {p}"
    elif sc < -40 and t == "DOWN":
        return f"🔻 STRONG SELL\n{s}\nPrice: {p}"
    else:
        return f"⚪ NO TRADE\n{s}"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    msg = get_signal()
    print(msg)
    send(msg)
