import pandas as pd
from strategy import calculate, spot_signal


def backtest(df):

    df = calculate(df)

    wins = 0
    losses = 0
    trades = 0

    for i in range(50, len(df)-1):

        sub = df.iloc[:i]

        sig, tp, sl = spot_signal(sub)

        if sig is None:
            continue

        entry = sub.iloc[-1]["close"]
        future = df.iloc[i+1:i+10]

        trades += 1

        hit_tp = any(future["close"] >= tp)
        hit_sl = any(future["close"] <= sl)

        if hit_tp and not hit_sl:
            wins += 1
        elif hit_sl and not hit_tp:
            losses += 1

    winrate = (wins / trades * 100) if trades > 0 else 0

    return {
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }
