def score_row(row):
    score = 50

    # RSI
    if row["rsi"] < 30:
        score += 10
    elif row["rsi"] > 70:
        score -= 10

    # MACD
    if row["macd"] > row["macd_signal"]:
        score += 15
    else:
        score -= 15

    # ADX trend strength
    if row["adx"] > 25:
        score += 10

    return max(0, min(100, score))
