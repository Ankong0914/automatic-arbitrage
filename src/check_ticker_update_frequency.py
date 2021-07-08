from exchanges.bit_flyer import BitFlyer
from exchanges.gmo_coin import GmoCoin
from exchanges.coin_check import CoinCheck
from exchanges.liquid import Liquid
from exchanges.ticker import Ticker

import time
from copy import copy

def wait_until_next_loop(start, duration):
    end = time.time()
    time.sleep(max(0, duration - (end - start)))


if __name__ == "__main__":
    DURATION = 20
    LOOP_DURATION = 0.1
    LOOP_NUM = DURATION / LOOP_DURATION
    i = 0
    count = 0
    exc = Liquid()
    pre_ts = exc.ticker.timestamp
    
    while i < LOOP_NUM:
        start = time.time()
        exc.fetch_ticker()
        ts = exc.ticker.timestamp
        print(ts, pre_ts)
        if ts != pre_ts:
            count += 1
            pre_ts = ts
        i += 1
        wait_until_next_loop(start, LOOP_DURATION)
    
    freq = count / DURATION
    print(f"{freq} times/sec")
