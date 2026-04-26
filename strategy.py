import ta

def calculate(df):

    df["ema20"] = ta.trend.ema_indicator(df["close"], 20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)

    df["rsi"] = ta.momentum.rsi(df["close"], 14)

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    return df


def spot_signal(df):

    last = df.iloc[-1]
    prev = df.iloc[-2]

    dip = last["rsi"] < 45
    tepe = last["rsi"] > 55

    bull = last["ema20"] > last["ema50"]
    bear = last["ema20"] < last["ema50"]

    if dip and bull:
        return "BUY", last["close"] * 1.02, last["close"] * 0.98

    if tepe and bear:
        return "SELL", last["close"] * 0.98, last["close"] * 1.02

    return None, None, None


def futures_signal(df):

    last = df.iloc[-1]

    if last["ema20"] > last["ema50"] and last["rsi"] < 50:
        return "LONG"

    if last["ema20"] < last["ema50"] and last["rsi"] > 50:
        return "SHORT"

    return None
