import requests
import time

# =========================
# AYARLAR (BURAYI DOLDUR)
# =========================
BOT_TOKEN = "BURAYA_BOT_TOKEN"
CHAT_ID = "BURAYA_CHAT_ID"

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram error")

# =========================
# BINANCE DATA (SAFE)
# =========================
def get_tickers():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()

        if not isinstance(data, list):
            return []

        return data
    except:
        return []

# =========================
# KLINE DATA
# =========================
def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        r = requests.get(url, timeout=10)
        data = r.json()

        if not isinstance(data, list):
            return []

        closes = [float(x[4]) for x in data if isinstance(x, list)]
        return closes
    except:
        return []

# =========================
# EMA
# =========================
def ema(data, period):
    if len(data) == 0:
        return 0

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

    if change > 5:
        s += 20
    elif change > 2:
        s += 10
    elif change < -5:
        s -= 20
    elif change < -2:
        s -= 10

    if volume > 1_000_000_000:
        s += 20
    elif volume > 500_000_000:
        s += 10
    elif volume < 100_000_000:
        s -= 10

    return s

# =========================
# TREND ANALİZ
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
    else:
        return "SIDE"

# =========================
# SİNYAL
# =========================
def get_signal():
    data = get_tickers()

    if not data:
        return "❌ DATA YOK"

    best = None
    best_score = -999

    for d in data:

        if not isinstance(d, dict):
            continue

        symbol = d.get("symbol")

        if not symbol or "USDT" not in symbol:
            continue

        try:
            change = float(d.get("priceChangePercent", 0))
            volume = float(d.get("quoteVolume", 0))
            price = float(d.get("lastPrice", 0))
        except:
            continue

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
        return "⚠️ COIN YOK"

    s, p, sc, t = best

    if sc >= 60 and t == "UP":
        return f"🔥 STRONG BUY\n{s}\nPrice: {p}\nScore: {sc}"

    elif sc <= -40 and t == "DOWN":
        return f"🔻 STRONG SELL\n{s}\nPrice: {p}\nScore: {sc}"

    else:
        return f"⚪ NO TRADE\n{s}\nScore: {sc}"

# =========================
# LOOP (5 DK)
# =========================
print("BOT STARTED")

while True:
    try:
        signal = get_signal()
        print(signal)
        send(signal)
    except Exception as e:
        print("ERROR:", e)

    time.sleep(300)
