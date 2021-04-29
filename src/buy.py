from exchanges.liquid import Liquid
from exchanges.coin_check import CoinCheck
import time

liq = Liquid()
cc = CoinCheck()

side = "market_buy"
LOOP_DURATION = 1

def wait_until_next_loop(start):
    end = time.time()
    time.sleep(max(0, LOOP_DURATION - (end - start)))

for i in range(20):
    start = time.time()
    cc.update_ticker()
    print(cc.ask, cc.timestamp)
    wait_until_next_loop(start)

order_s = time.time()
print(f"ask at ordering: {cc.ask}")
print(f"time of sending an order: {order_s}")
# size = cc.MIN_TRANS_UNIT * cc.ask * 1.01
# cc.post_order(side, size)
order_e = time.time()
print(f"time of receiving a response: {order_e}")
print(f"time for contract: {order_e - order_s}")

for i in range(20):
    start = time.time()
    cc.update_ticker()
    print(cc.ask, cc.timestamp)
    wait_until_next_loop(start)