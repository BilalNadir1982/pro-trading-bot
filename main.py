import requests
import pandas as pd
import numpy as np
import ta
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
# COINGECKO DATA
# =========================
def get_data():

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }

    r = requests.get(URL, params=params)

    if r.status_code != 200:
        return []

    return r.json()

# =========================
# SCORE ENGINE
# =========================
def score_coin(change, volume):

    score = 50

    if 3 < change < 10:
        score += 25

    elif 1 < change <= 3:
        score += 15

    elif change < -5:
        score -= 20

    if volume > 5_000_000_000:
        score += 25

    elif volume > 1_000_000_000:
        score += 15

    elif volume < 100_000_000:
        score -= 15

    return max(0, min(100, score))

# =========================
# SIGNAL ENGINE
# =========================
def scan():

    data = get_data()

    coins = []

    BAD = ["usdc", "usdt", "busd", "dai"]

    for d in data:

        try:
            symbol = d["symbol"].upper()

            if symbol.lower() in BAD:
                continue

            price = float(d["current_price"])
            change = float(d["price_change_percentage_24h"] or 0)
            volume = float(d["total_volume"] or 0)

            score = score_coin(change, volume)

            signal = "WATCH"

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
                "price": price,
                "change": round(change, 2),
                "score": score,
                "signal": signal
            })

        except:
            continue

    coins = sorted(coins, key=lambda x: x["score"], reverse=True)

    return coins[:5]

# =========================
# MAIN LOOP
# =========================
send("🚀 PRO COINGECKO BOT STARTED")

while True:

    try:

        coins = scan()

        for c in coins:

            msg = f"""
{c['signal']}

💎 Coin: {c['symbol']}
💰 Price: {c['price']}
📊 Score: {c['score']}
📈 24H: {c['change']}%
"""

            send(msg)

        time.sleep(1800)

    except Exception as e:
        print(e)
        time.sleep(60)
