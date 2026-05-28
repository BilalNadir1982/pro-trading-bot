import os
import requests
import asyncio
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)
URL = "https://api.coingecko.com/api/v3/coins/markets"

async def send_msg(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
        print(f"[TELEGRAM] Sent:\n{msg}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

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
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def score_coin(change, volume, btc_change):
    score = 50
    if 4 <= change <= 10: score += 30
    elif 2 <= change < 4: score += 20
    elif 0.5 <= change < 2: score += 10
    elif -1 <= change < 0.5: score -= 10
    elif change < -3: score -= 25

    if volume > 10_000_000_000: score += 25
    elif volume > 3_000_000_000: score += 15
    elif volume < 100_000_000: score -= 15

    if btc_change < -2: score -= 15
    return max(0, min(100, score))

def scan():
    data = get_data()
    if not data: return []

    coins = []
    btc_change = 0

    for d in data:
        try:
            if d["symbol"].lower() == "btc":
                btc_change = float(d["price_change_percentage_24h"] or 0)
                break
        except: continue

    BAD_COINS = ["usdt", "usdc", "busd", "dai", "tusd", "fdusd", "wbtc"]

    for d in data:
        try:
            symbol = d["symbol"].upper()
            if symbol.lower() in BAD_COINS: continue

            price = float(d["current_price"] or 0)
            change = float(d["price_change_percentage_24h"] or 0)
            volume = float(d["total_volume"] or 0)

            if volume < 100_000_000 or change > 20: continue

            score = score_coin(change, volume, btc_change)

            # Sadece güçlü ve net sinyalleri kanala raporla (Gereksiz WATCH mesajlarını eliyoruz)
            if score >= 85: signal = "🚀 *ULTRA LONG*"
            elif score >= 70: signal = "🔥 *STRONG BUY*"
            elif score <= 35: signal = "🔻 *SELL*"
            else: continue 

            coins.append({
                "symbol": symbol, "price": price, "change": round(change, 2),
                "volume": volume, "score": score, "signal": signal
            })
        except: continue

    return sorted(coins, key=lambda x: x["score"], reverse=True)[:5]

async def main():
    print("[INFO] Piyasa taraması başlatılıyor...")
    coins = scan()

    if not coins:
        print("[INFO] Kriterlere uyan keskin bir sinyal bulunamadı.")
        return

    for c in coins:
        msg = f"""{c['signal']}

💎 *Coin:* #{c['symbol']}
💰 *Fiyat:* ${c['price']:,}
📈 *24H Değişim:* {c['change']}%
📊 *Yapar Zeka Skoru:* {c['score']}/100
"""
        await send_msg(msg)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
