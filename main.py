print("BOT STARTED")
import pandas as pd
import requests

df = get_data(symbol)

if df is None:
    continue
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "limit": 200}

    data = requests.get(url, params=params).json()

    # ❗ HATA KONTROL
    if not isinstance(data, list) or len(data) == 0:
        return None

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "_","_","_","_","_","_"
    ])

    df = df[["open","high","low","close","volume"]]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def run():
    sent = {}

    while True:
        try:
            for symbol in SYMBOLS:

    df = get_data(symbol)

    if df is None:
        continue

    df = calculate(df)

    sig, tp, sl = signal(df)

    if sig:
        key = f"{symbol}_{sig}"

        if key not in sent:
            price = df.iloc[-1]["close"]

            msg = f"""
🚀 SİNYAL

Coin: {symbol}
Tip: {sig}
Entry: {price}

TP: {round(tp,2)}
SL: {round(sl,2)}
"""
            send(msg)
            sent[key] = True

            time.sleep(60)

        except Exception as e:
            print(e)
            time.sleep(10)

run()
