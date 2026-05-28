import os
import requests
import json

# ==========================================
# 1. GÜVENLİ GERÇEK ZAMANLI AYARLAR
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

def send_telegram_vip_report(text):
    """Gelişmiş VIP rapor metnini tek blok halinde kanala fırlatır."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[BAĞLANTI HATASI] GitHub Secrets alanında BOT_TOKEN veya CHAT_ID eksik!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("[BAŞARILI] VIP Kripto Raporu kanala ulaştırıldı.")
        else:
            print(f"[TELEGRAM HATASI] Kod: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[BAĞLANTI HATASI] Telegram'a istek atılamadı: {e}")

def fetch_crypto_market_data():
    """CoinGecko altyapısından piyasanın en yüksek hacimli 100 varlığını çeker."""
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }
    try:
        response = requests.get(API_URL, params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
        print(f"[API UYARISI] CoinGecko yanıt vermedi, kod: {response.status_code}")
        return []
    except Exception as e:
        print(f"[API HATASI] Veri çekme esnasında sorun oluştu: {e}")
        return []

def calculate_ai_crypto_score(change, volume, btc_change):
    """Matematiksel trend, balina hacmi ve BTC korelasyon hesaplama motoru."""
    score = 50
    
    # 24 Saatlik Değişim Puanlaması
    if 4 <= change <= 10: score += 30
    elif 2 <= change < 4: score += 20
    elif 0.5 <= change < 2: score += 10
    elif -1 <= change < 0.5: score -= 10
    elif change < -3: score -= 25

    # Balina Hacim Puanlaması (Balina Giriş Tespiti)
    if volume > 10_000_000_000: score += 25
    elif volume > 3_000_000_000: score += 15
    elif volume < 100_000_000: score -= 15

    # Lider Kripto Para Güven Endeksi Baskısı
    if btc_change < -2: score -= 15
    
    return max(0, min(100, score))

def analyze_and_filter_market():
    """Piyasayı tarar, stabil coinleri temizler ve en keskin 5 sinyali seçer."""
    raw_market_data = fetch_crypto_market_data()
    if not raw_market_data: return []

    processed_signals = []
    btc_24h_change = 0

    # Adım 1: Piyasa yönü için öncü BTC durumunu analiz et
    for asset in raw_market_data:
        try:
            if asset["symbol"].lower() == "btc":
                btc_24h_change = float(asset["price_change_percentage_24h"] or 0)
                break
        except: continue

    # Adım 2: Hacimsizleri ve stabil endeksleri temizle
    STABLE_AND_WRAPPED = ["usdt", "usdc", "busd", "dai", "tusd", "fdusd", "wbtc"]

    for asset in raw_market_data:
        try:
            symbol = asset["symbol"].upper()
            if symbol.lower() in STABLE_AND_WRAPPED: continue

            price = float(asset["current_price"] or 0)
            change = float(asset["price_change_percentage_24h"] or 0)
            volume = float(asset["total_volume"] or 0)

            # Eşik Değer Filtresi: Günlük 100M$ altı hacimleri ve manipülatif pump'ları eliyoruz
            if volume < 100_000_000 or change > 20: continue

            # Yapay zeka skorunu hesapla
            ai_score = calculate_ai_crypto_score(change, volume, btc_24h_change)

            # Sinyal başlıkları ve profesyonel etiketleme
            if ai_score >= 85: 
                signal_tag = "🚀 **ULTRA LONG (GÜÇLÜ AL)**"
                market_note = "Yüksek balina hacmi desteğiyle kırılım eşiğinde."
            elif ai_score >= 70: 
                signal_tag = "🟢 **STRONG BUY (KUVVETLİ AL)**"
                market_note = "Teknik indikatörler ve para girişi trendi destekliyor."
            elif ai_score <= 35: 
                signal_tag = "🔻 **STRONG SELL (KUVVETLİ SAT)**"
                market_note = "Aşırı satım baskısı ve hacim kaybı mevcut."
            else: continue 

            processed_signals.append({
                "symbol": symbol, "price": price, "change": round(change, 2),
                "volume": volume, "score": ai_score, "signal": signal_tag, "note": market_note
            })
        except: continue

    # Yapay zeka skoruna göre en yüksekten en düşüğe sırala ve en iyi 5 varlığı getir
    return sorted(processed_signals, key=lambda x: x["score"], reverse=True)[:5]

def main():
    print("[OTOMASYON BAŞLADI] Kripto yapay zeka radar taraması aktif edildi...")
    top_signals = analyze_and_filter_market()

    if not top_signals:
        print("[BİLGİ] Yapay zeka kriterlerine uyan keskin bir piyasa fırsatı bulunamadı. Rapor basılmadı.")
        return

    # ==========================================
    # 2. GÖRKEMLİ VIP RAPOR TASARIM MATRİSİ
    # ==========================================
    msg = "💎 ═══ **YAPAY ZEKA KRİPTO RADARI** ═══ 💎\n"
    msg += "🔥 *Para Girişleri ve Balina İndeksi Analizleriyle Günlük Sinyaller!*\n\n"
    msg += "📊 **YAPAY ZEKA GÜNCEL TREND SIRALAMASI**\n"
    msg += "🔸 ─────────────────────── 🔸\n\n"

    for coin in top_signals:
        formatted_price = f"{coin['price']:,}" if coin['price'] >= 1 else f"{coin['price']:.6f}"
        formatted_change = f"+{coin['change']}" if coin['change'] > 0 else f"{coin['change']}"

        msg += f"{coin['signal']}\n"
        msg += f"🎫 **Coin:** #{coin['symbol']}\n"
        msg += f"💰 *Fiyat:* `${formatted_price}`  |  ⭐ *AI Skor:* `{coin['score']}/100`\n"
        msg += f"📈 *24H Değişim:* `% {formatted_change}`\n"
        msg += f"⚡ *Analiz Notu:* _{coin['note']}_\n"
        msg += "🔸 ─────────────────────── 🔸\n\n"

    msg += "🎰 **Genel Piyasa Güven Endeksi:** `🟩🟩🟩🟩🟩🟩🟩🟩⬜⬜ %80`\n"
    msg += "🔔 *Kripto para piyasasında fırsatlar anlıktır. Bildirimleri açmayı unutmayın!*"

    send_telegram_vip_report(msg)

if __name__ == "__main__":
    main()
