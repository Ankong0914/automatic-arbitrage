from exchanges.coin_check import CoinCheck
from exchanges.liquid import Liquid
import pandas as pd
import time
import asyncio
import logging
import requests
import csv

# logging.basicConfig(level=logging.INFO)

class Arbitrage():
    def __init__(self, exc1, exc2):
        self.logger = logging.getLogger(__name__)
        self.exc1 = exc1
        self.exc2 = exc2
        self.high_ask_exc = None
        self.low_ask_exc = None
        self.LOOP_DURATION = 1.0 # TODO
        self.MIN_TRANS_UNIT = min([self.exc1.MIN_TRANS_UNIT, self.exc2.MIN_TRANS_UNIT])

    async def update_tickers(self, exc1, exc2):  # TODO: more generalize
        loop = asyncio.get_event_loop()
        future1 = loop.run_in_executor(None, exc1.update_ticker)
        future2 = loop.run_in_executor(None, exc2.update_ticker)
        await future1
        await future2

    def send_async_requests(self, func, args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args))

    def get_relation(self):
        if self.exc1.ask > self.exc2.ask:
            self.high_ask_exc, self.low_ask_exc = self.exc1, self.exc2
        else:
            self.high_ask_exc, self.low_ask_exc = self.exc2, self.exc1

        if self.high_ask_exc.bid > self.low_ask_exc.ask:
            relation = "gap"
        elif self.high_ask_exc.bid >= self.low_ask_exc.bid:
            relation = "intersection"
        else:
            relation = "inclusion"
        return relation
    
    def calc_margin(self):
        selling_price = self.high_ask_exc.bid
        selling_charge = selling_price * self.high_ask_exc.TRANS_CHARGE_RATE
        buying_price = self.low_ask_exc.ask
        buying_charge = buying_price * self.low_ask_exc.TRANS_CHARGE_RATE
        margin = selling_price - buying_price - selling_charge - buying_charge
        return margin

    def get_margin_type(self, margin):
        MARGIN_THRES_RATE = [0.0002, 0.0007, 0.0012, 0.0018] # 2100, 4900, 8400, 12600 

        if margin < MARGIN_THRES_RATE[0] * self.high_ask_exc.ask:
            margin_type = "little"
        elif margin < MARGIN_THRES_RATE[1] * self.high_ask_exc.ask:
            margin_type = "small"
        elif margin < MARGIN_THRES_RATE[2] * self.high_ask_exc.ask:
            margin_type = "mid"
        elif margin < MARGIN_THRES_RATE[3] * self.high_ask_exc.ask:
            margin_type = "large"
        else:
            margin_type = "huge"
        return margin_type

    def get_size(self, margin_type):
        target_btc_ratio = {}
        target_btc_ratio["small"] = 4/8
        target_btc_ratio["mid"] = 5/8
        target_btc_ratio["large"] = 7/8
        target_btc_ratio["huge"] = 8/8

        total_btc = self.exc1.balance_btc + self.exc2.balance_btc
        size = total_btc * target_btc_ratio[margin_type] - self.low_ask_exc.balance_btc
        if size < self.MIN_TRANS_UNIT:
            size = 0
        return size

    def wait_until_next_loop(self, start):
        end = time.time()
        time.sleep(max(0, self.LOOP_DURATION - (end - start)))

    def run(self):
        while True:
            start = time.time()

            # update tickers
            self.send_async_requests(self.update_tickers, (self.exc1, self.exc2))

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                self.wait_until_next_loop(start)
                continue

            margin = self.calc_margin()
            margin_type = self.get_margin_type(margin)  # little ~ huge
            if margin_type == "little":
                self.wait_until_next_loop(start)
                continue

            size = self.get_size(margin_type) 
            if size == 0:
                self.wait_until_next_loop(start)
                continue

            # order TODO: asyncronize
            # self.high_ask_exc.post_order("SELL", size)
            # self.low_ask_exc.post_order("BUY", size)

            # get balance TODO: asyncronize
            self.exc1.update_balance() # need not do this here
            self.exc2.update_balance()

            self.wait_until_next_loop(start)
    

class ArbitrageSimulator(Arbitrage):
    def __init__(self, exc1, exc2):
        super(ArbitrageSimulator, self).__init__(exc1, exc2)
        self.exc1.balance_jpy = 250000
        self.exc1.balance_btc = 0.02
        self.exc2.balance_jpy = 250000
        self.exc2.balance_btc = 0.02
        self.chart = {}
        self.chart[self.exc1.NAME] = pd.read_csv(f"../data/chart_{self.exc1.NAME}.csv")
        self.chart[self.exc2.NAME] = pd.read_csv(f"../data/chart_{self.exc2.NAME}.csv")
    
    def simulated_order(self, size):
        self.high_ask_exc.balance_jpy += self.high_ask_exc.bid * size
        self.high_ask_exc.balance_btc -= size
        self.low_ask_exc.balance_jpy -= self.low_ask_exc.ask * size
        self.low_ask_exc.balance_btc += size

    def update_tickers_from_charts(self, tickers):
        self.exc1.ask = tickers[0].ask
        self.exc1.bid = tickers[0].bid
        self.exc1.timestamp = tickers[0].timestamp

        self.exc2.ask = tickers[1].ask
        self.exc2.bid = tickers[1].bid
        self.exc2.timestamp = tickers[1].timestamp
    
    def record_order(self):
        with open("../data/order_record.csv", "a") as f:
            w = csv.writer(f, delimiter=",")
            profit = int(self.exc1.balance_jpy + self.exc2.balance_jpy - 500000)
            w.writerow([profit, self.exc2.timestamp])

    def simulate(self):
        charts_iter = zip(self.chart[self.exc1.NAME].itertuples(), self.chart[self.exc2.NAME].itertuples())
        for ticker1, ticker2 in charts_iter:
            # update ticker
            self.update_tickers_from_charts([ticker1, ticker2])

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                continue

            margin = self.calc_margin()
            margin_type = self.get_margin_type(margin)  # little ~ ultra
            if margin_type == "little":
                continue

            size = self.get_size(margin_type)  # 0 ~ 13
            if size == 0:
                continue
            
            self.simulated_order(size)
            profit = int(self.exc1.balance_jpy + self.exc2.balance_jpy - 500000)
            print(profit, margin_type, size, self.exc1.balance_btc, self.exc2.balance_btc)
        
    def simulate_realtime(self):
        while True:
            start = time.time()

            # update tickers
            try:
                self.send_async_requests(self.update_tickers, (self.exc1, self.exc2))
            except requests.exceptions.RequestException as e:
                self.wait_until_next_loop(start)
                continue

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                self.wait_until_next_loop(start)
                continue

            margin = self.calc_margin()
            margin_type = self.get_margin_type(margin)  # little ~ huge
            if margin_type == "little":
                self.wait_until_next_loop(start)
                continue

            size = self.get_size(margin_type) 
            if size == 0:
                self.wait_until_next_loop(start)
                continue

            self.simulated_order(size)
            self.record_order()

            # get balance TODO: asyncronize
            self.exc1.update_balance() # need not do this here
            self.exc2.update_balance()

            self.wait_until_next_loop(start)


if __name__ == "__main__":
    cc = CoinCheck()
    liq = Liquid()
    arbit_sim = ArbitrageSimulator(cc, liq)
    arbit_sim.simulate()
