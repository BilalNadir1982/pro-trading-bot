import time

last_signal = {}

def allow(symbol):
    now = time.time()
    if symbol in last_signal:
        if now - last_signal[symbol] < 900:  # 15 min
            return False

    last_signal[symbol] = now
    return True
