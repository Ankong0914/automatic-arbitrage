import time

from exchanges.coin_check import CoinCheck
from exchanges.liquid import Liquid
from exchanges.gmo_coin import GmoCoin
from exchanges.bit_flyer import BitFlyer

LOOP_DURATION = 1

def wait_until_next_loop(start):
    end = time.time()
    time.sleep(max(0, LOOP_DURATION - (end - start)))

cc = CoinCheck()
liq = Liquid()
gc = GmoCoin()

while True:
    start = time.time()

    cc.fetch_ticker()
    liq.fetch_ticker()
    gc.fetch_ticker()

    cc.put_ticker_to_db()
    liq.put_ticker_to_db()
    gc.put_ticker_to_db()

    wait_until_next_loop(start)