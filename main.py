from flask import Flask, request
import requests

app = Flask(__name__)

# TELEGRAM
TOKEN = "BURAYA_BOT_TOKEN"
CHAT_ID = "BURAYA_CHAT_ID"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    signal = data.get("signal")
    symbol = data.get("symbol")
    price  = data.get("price")

    if signal == "BUY":
        text = f"""
🟢 AL SİNYALİ

📊 {symbol}
💰 {price}

📈 Trend Uyumlu Dip
"""
    else:
        text = f"""
🔴 SAT SİNYALİ

📊 {symbol}
💰 {price}

📉 Tepe Satışı
"""

    send(text)
    return {"ok": True}

app.run(host="0.0.0.0", port=10000)
