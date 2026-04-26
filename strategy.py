import ta

def calculate(df):
    df["ema20"] = ta.trend.ema_indicator(df["close"], 20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)

    df["rsi"] = ta.momentum.rsi(df["close"], 14)

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    return df


def signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    dip = prev["rsi"] < 35 and last["rsi"] > prev["rsi"]
    tepe = prev["rsi"] > 65 and last["rsi"] < prev["rsi"]

    bull = last["ema20"] > last["ema50"]
    bear = last["ema20"] < last["ema50"]

    if dip and bull and last["macd"] > last["macd_signal"]:
        return "BUY", last["close"] * 1.02, last["close"] * 0.98

    if tepe and bear and last["macd"] < last["macd_signal"]:
        return "SELL", last["close"] * 0.98, last["close"] * 1.02

    return None, None, None
