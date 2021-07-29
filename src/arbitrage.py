import pandas as pd
import time
import datetime
import asyncio
import logging
import requests
import csv

from exchanges.coin_check import CoinCheck
from exchanges.liquid import Liquid
from exchanges.gmo_coin import GmoCoin
from exchanges.utils import send_async_requests

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

    def get_relation(self):
        if self.exc1.ticker.ask > self.exc2.ticker.ask:
            self.high_ask_exc, self.low_ask_exc = self.exc1, self.exc2
        else:
            self.high_ask_exc, self.low_ask_exc = self.exc2, self.exc1

        if self.high_ask_exc.ticker.bid > self.low_ask_exc.ticker.ask:
            relation = "gap"
        elif self.high_ask_exc.ticker.ask >= self.low_ask_exc.ticker.bid:
            relation = "intersection"
        else:
            relation = "inclusion"
        return relation
    
    def calc_margin(self):
        selling_price = self.high_ask_exc.ticker.bid
        selling_charge = selling_price * self.high_ask_exc.trans_charge_rate
        buying_price = self.low_ask_exc.ticker.ask
        buying_charge = buying_price * self.low_ask_exc.trans_charge_rate
        margin = selling_price - buying_price - selling_charge - buying_charge
        return margin

    def get_margin_type(self, margin):
        MARGIN_THRES_RATE = [0.0003, 0.0006, 0.0009, 0.0012] # 2100, 4900, 8400, 12600 

        if margin < MARGIN_THRES_RATE[0] * self.high_ask_exc.ticker.ask:
            margin_type = "little"
        elif margin < MARGIN_THRES_RATE[1] * self.high_ask_exc.ticker.ask:
            margin_type = "small"
        elif margin < MARGIN_THRES_RATE[2] * self.high_ask_exc.ticker.ask:
            margin_type = "mid"
        elif margin < MARGIN_THRES_RATE[3] * self.high_ask_exc.ticker.ask:
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

        total_btc = self.exc1.account.balance["BTC"] + self.exc2.account.balance["BTC"]
        size = total_btc * target_btc_ratio[margin_type] - self.low_ask_exc.account.balance["BTC"]
        if size < self.MIN_TRANS_UNIT:
            size = 0
        return round(size, 8)
    
    def fetch_simul_tickers(self):
        funcs = (self.exc1.ticker.fetch, self.exc2.ticker.fetch)
        send_async_requests(funcs)
    
    def fetch_simul_balances(self):
        funcs = (self.exc1.account.fetch_balance, self.exc2.account.fetch_balance)
        send_async_requests(funcs)
    
    def make_simul_transactions(self, sell_order, buy_order):
        # send orders
        funcs = (sell_order.send, buy_order.send)
        sell_order_id, buy_order_id = send_async_requests(funcs)

        # get transactions
        funcs = (self.high_ask_exc.get_transaction_result, self.low_ask_exc.get_transaction_result)
        args = ((sell_order_id,), (buy_order_id,))
        sell_result, buy_result = send_async_requests(funcs, args)
        return sell_result, buy_result
    
    def show_contract_result(self, sell_result, buy_result):
        timestamp = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        buy_exc = self.low_ask_exc.NAME
        sell_exc = self.high_ask_exc.NAME
        sell_price, buy_price, sell_size, buy_size = 0, 0, 0, 0
        for sr in sell_result:
            sell_price += sr["price"] * sr["size"]
            sell_size += sr["size"]
        sell_rate = sell_price / sell_size
        sell_rate_diff = self.high_ask_exc.ticker["bid"] - sell_rate 
        for br in buy_result:
            buy_price += br["price"] * br["size"]
            buy_size += br["size"]
        buy_rate = buy_price / buy_size
        buy_rate_diff = self.low_ask_exc.ticker["ask"] - buy_rate
        margin = sell_price - buy_price
        size_diff = round(buy_size - sell_size, 7)


        result = {
            "timestamp": timestamp,
            "buy": f"{int(buy_price)} jpy | {buy_size} btc | {int(buy_rate)} jpy/btc ({sell_rate_diff}) @ {buy_exc}",
            "sell": f"{int(sell_price)} jpy | {sell_size} btc | {int(sell_rate)} jpy/btc ({buy_rate_diff}) @ {sell_exc}",
            "margin": f"{int(margin)} ({size_diff} btc)"
        }

        # print contract result
        key_width = max([len(key) for key in result.keys()])
        print("="*50)
        for key, value in result.items():
            print(f"{key.ljust(key_width)}: {value}")
        print("*"*50)
 
    def wait_until_next_loop(self, start):
        end = time.time()
        time.sleep(max(0, self.LOOP_DURATION - (end - start)))

    def run(self):
        print("start run")
        self.fetch_simul_balances()
        
        while True:
            start = time.time()

            # fetch tickers
            self.fetch_simul_tickers()

            relation = self.get_relation()  # gap/intersection/inclusion
            print(f"{relation} / {self.high_ask_exc.NAME} - {self.low_ask_exc.NAME}")
            if relation != "gap":
                self.wait_until_next_loop(start)
                continue

            margin = self.calc_margin()
            margin_type = self.get_margin_type(margin)  # little ~ huge
            print(margin_type, margin)
            if margin_type == "little":
                self.wait_until_next_loop(start)
                continue

            size = self.get_size(margin_type) 
            print(size)
            if size == 0:
                self.wait_until_next_loop(start)
                continue
            
            size = self.MIN_TRANS_UNIT
            new_sell_order = self.high_ask_exc.create_order(self.high_ask_exc.order_type, "sell", size, price=self.high_ask_exc.ticker.bid)
            new_buy_order = self.low_ask_exc.create_order(self.low_ask_exc.order_type, "buy", size, price=self.low_ask_exc.ticker.ask)
            sell_result, buy_result = self.make_simul_transactions(new_buy_order, new_sell_order)
            print(margin)
            self.show_contract_result(sell_result, buy_result)

    
if __name__ == "__main__":
    gc = GmoCoin()
    liq = Liquid()
    arbitrage = Arbitrage(gc, liq)
    arbitrage.run()
