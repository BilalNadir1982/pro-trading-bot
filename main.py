import requests
import time
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)

URL = "https://api.coingecko.com/api/v3/coins/markets"

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# =========================
# MEMORY
# =========================
sent_signals = {}

# =========================
# GET DATA
# =========================
def get_data():

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }

    try:
        r = requests.get(URL, params=params, timeout=20)

        if r.status_code != 200:
            return []

        return r.json()

    except:
        return []

# =========================
# SCORE SYSTEM
# =========================
def score_coin(change, volume, btc_change):

    score = 50

    # =====================
    # PRICE ACTION
    # =====================
    if 4 <= change <= 10:
        score += 30

    elif 2 <= change < 4:
        score += 20

    elif 0.5 <= change < 2:
        score += 10

    elif -1 <= change < 0.5:
        score -= 10

    elif change < -3:
        score -= 25

    # =====================
    # VOLUME
    # =====================
    if volume > 10_000_000_000:
        score += 25

    elif volume > 3_000_000_000:
        score += 15

    elif volume < 100_000_000:
        score -= 15

    # =====================
    # BTC FILTER
    # =====================
    if btc_change < -2:
        score -= 15

    return max(0, min(100, score))

# =========================
# SIGNAL ENGINE
# =========================
def scan():

    data = get_data()

    if not data:
        return []

    coins = []

    # =====================
    # BTC MARKET FILTER
    # =====================
    btc_change = 0

    for d in data:

        try:
            if d["symbol"].lower() == "btc":
                btc_change = float(d["price_change_percentage_24h"] or 0)
                break

        except:
            continue

    # =====================
    # BAD COINS
    # =====================
    BAD = [
        "usdt",
        "usdc",
        "busd",
        "dai",
        "tusd",
        "fdusd"
    ]

    # =====================
    # SCAN
    # =====================
    for d in data:

        try:

            symbol = d["symbol"].upper()

            if symbol.lower() in BAD:
                continue

            price = float(d["current_price"] or 0)
            change = float(d["price_change_percentage_24h"] or 0)
            volume = float(d["total_volume"] or 0)

            # LOW VOLUME FILTER
            if volume < 100_000_000:
                continue

            # EXTREME PUMP FILTER
            if change > 20:
                continue

            score = score_coin(change, volume, btc_change)

            # =====================
            # SIGNALS
            # =====================
            signal = "⚪ WATCH"

            if score >= 85:
                signal = "🚀 ULTRA LONG"

            elif score >= 70:
                signal = "🔥 STRONG BUY"

            elif score >= 60:
                signal = "🟢 BUY"

            elif score <= 35:
                signal = "🔻 SELL"

            coins.append({
                "symbol": symbol,
                "price": round(price, 4),
                "change": round(change, 2),
                "volume": volume,
                "score": score,
                "signal": signal
            })

        except:
            continue

    coins = sorted(coins, key=lambda x: x["score"], reverse=True)

    return coins[:5]

# =========================
# START
# =========================
send("🚀 PRO COINGECKO BOT STARTED")

# =========================
# LOOP
# =========================
while True:

    try:

        coins = scan()

        if not coins:
            send("❌ DATA ERROR")
            time.sleep(300)
            continue

        for c in coins:

            # SPAM FILTER
            last_signal = sent_signals.get(c["symbol"])

            if last_signal == c["signal"]:
                continue

            sent_signals[c["symbol"]] = c["signal"]

            msg = f"""
{c['signal']}

💎 Coin: {c['symbol']}
💰 Price: {c['price']}
📈 24H: {c['change']}%
📊 Score: {c['score']}
"""

            send(msg)

        # 30 dakika
        time.sleep(1800)

    except Exception as e:

        print(e)

        time.sleep(60)
