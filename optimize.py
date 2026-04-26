def optimize_params():

    best = {"winrate": 0, "rsi": 0}

    for rsi_level in range(40, 60, 2):

        def test_rsi(df):

            last = df.iloc[-1]

            if last["rsi"] < rsi_level:
                return "BUY", None, None

            return None, None, None

        # fake score (basit test mantığı)
        score = rsi_level / 100

        if score > best["winrate"]:
            best["winrate"] = score
            best["rsi"] = rsi_level

    return best
