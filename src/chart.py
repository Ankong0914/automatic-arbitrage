import asyncio
import csv
import time

from exchanges.bit_flyer import BitFlyer
from exchanges.gmo_coin import GmoCoin


@asyncio.coroutine
def func1(exc, w, i):
    while True:
        exc.update_ticker()
        data = [i, exc.ask, exc.bid, exc.timestamp]
        w.writerow(data)
        i += 1
        yield from asyncio.sleep(1)


if __name__ == "__main__":
    bf = BitFlyer()
    gc = GmoCoin()

    with open("data/chart_bitflyer2.csv", "a") as f_bf, open("data/chart_gmocoin2.csv", "a") as f_gc:
        w_bf = csv.writer(f_bf, delimiter=",")
        w_bf.writerow(["index", "ask", "bid", "timestamp"])
        w_gc = csv.writer(f_gc, delimiter=",")
        w_gc.writerow(["index", "ask", "bid", "timestamp"])
        i = 0

        loop = asyncio.get_event_loop()
        tasks = asyncio.wait([func1(bf, w_bf, i), func1(gc, w_gc, i)])
        loop.run_until_complete(tasks)