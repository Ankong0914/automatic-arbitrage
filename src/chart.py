import asyncio
import csv
import time
import requests

from exchanges.coin_check import CoinCheck
from exchanges.liquid import Liquid


async def update_tickers(exc1, exc2):  # TODO: more generalize
    loop = asyncio.get_event_loop()
    future1 = loop.run_in_executor(None, exc1.update_ticker)
    future2 = loop.run_in_executor(None, exc2.update_ticker)
    await future1
    await future2

def send_async_requests(func, args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func(*args))


if __name__ == "__main__":
    cc = CoinCheck()
    liq = Liquid()
    
    i = 0

    with open("../data/chart_coincheck_test.csv", "a") as f_cc, open("../data/chart_liquid_test.csv", "a") as f_liq:
        w_cc = csv.writer(f_cc, delimiter=",")
        w_liq = csv.writer(f_liq, delimiter=",")
        w_cc.writerow(["index", "ask", "bid", "timestamp"])
        w_liq.writerow(["index", "ask", "bid", "timestamp"])
        
        while True:
            start = time.time()
            i += 1
            print(i)
            try:
                send_async_requests(update_tickers, (cc, liq))
            except requests.exceptions.RequestException as e:
                time.sleep(max(0, 1.1 - (end - start)))
                continue
            w_cc.writerow([i, cc.ask, cc.bid, cc.timestamp])
            w_liq.writerow([i, liq.ask, liq.bid, liq.timestamp])
            end = time.time()
            time.sleep(max(0, 1.1 - (end - start)))
