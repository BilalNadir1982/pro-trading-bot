import pandas as pd
import ta

def calculate(df):

    df["ema20"] = ta.trend.ema_indicator(df["close"], 20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], 200)

    df["rsi"] = ta.momentum.rsi(df["close"], 14)

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df["atr"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], 14)

    return df


def signal(df):

    last = df.iloc[-1]
    prev = df.iloc[-2]

    dip = prev["rsi"] < 35 and last["rsi"] > prev["rsi"]
    tepe = prev["rsi"] > 65 and last["rsi"] < prev["rsi"]

    bull = last["ema20"] > last["ema50"] > last["ema200"]
    bear = last["ema20"] < last["ema50"] < last["ema200"]

    if dip and bull and last["macd"] > last["macd_signal"]:
        tp = last["close"] + last["atr"] * 2
        sl = last["close"] - last["atr"] * 1.2
        return "BUY", tp, sl

    if tepe and bear and last["macd"] < last["macd_signal"]:
        tp = last["close"] - last["atr"] * 2
        sl = last["close"] + last["atr"] * 1.2
        return "SELL", tp, sl

    return None, None, None
