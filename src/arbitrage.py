from exchanges.bit_flyer import BitFlyer
from exchanges.gmo_coin import GmoCoin
import pandas as pd
import time
import asyncio


class Arbitrage():
    def __init__(self, exc1, exc2):
        self.exc1 = exc1
        self.exc2 = exc2
        self.high_ask_exc = None
        self.low_ask_exc = None
        self.LOOP_DURATION = 1.0
        self.trans_size_table = pd.read_csv("../data/transaction_size.csv")

    async def update_tickers(self, exc1, exc2):  # TODO: more generalize
        loop = asyncio.get_event_loop()
        future1 = loop.run_in_executor(None, exc1.update_ticker)
        future2 = loop.run_in_executor(None, exc2.update_ticker)
        await future1
        await future2

    def send_async_requests(self, func, args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args))

    def get_status(self):  # TODO: rename
        RATIO_THRES = 0.3
        RATIO_THRES_HEAVY = 0.5

        total_btc = self.exc1.balance_btc + self.exc2.balance_btc
        diff_btc = abs(self.exc1.balance_btc - self.exc2.balance_btc)

        if total_btc == 0:
            status = "balanced"
            return status

        ratio = diff_btc / total_btc
        if ratio < RATIO_THRES:
            status = "balanced"
        elif ratio < RATIO_THRES_HEAVY:
            status = "unbalanced"
        else:
            status = "unbalanced_heavy"
        return status

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

    def get_margin_expectation(self, margin):
        MARGIN_THRES = [1000, 5000, 10000, 15000]

        if margin < MARGIN_THRES[0]:
            expectation = "little"
        elif margin < MARGIN_THRES[1]:
            expectation = "low"
        elif margin < MARGIN_THRES[2]:
            expectation = "mid"
        elif margin < MARGIN_THRES[3]:
            expectation = "high"
        else:
            expectation = "ultra"
        return expectation

    def get_approach(self):
        if self.high_ask_exc.balance_btc > self.low_ask_exc.balance_btc:
            approach = "level"
        else:
            approach = "tilt"
        return approach

    def get_size(self, expectation, status, approach):
        trans_size = self.trans_size_table[
                        (self.trans_size_table["expectation"] == expectation) &
                        (self.trans_size_table["credit_status"] == status) &
                        (self.trans_size_table["approach"] == approach)
                    ]["credit_size"].values[0]
        return trans_size

    def simulated_order(self, trans_size):
        self.high_ask_exc.jpy += self.high_ask_exc.bid * trans_size
        self.high_ask_exc.btc -= trans_size
        self.low_ask_exc.jpy -= self.low_ask_exc.ask * trans_size
        self.low_ask_exc.btc += trans_size
    
    def show_trans_result(self):
        print("-------------------------------")
        profit = self.exc1.balance_jpy + self.exc2.balance_jpy - 500000
        print(f"profit :{profit}")
        print("-------------------------------")

    def wait_until_next_loop(self, start):
        end = time.time()
        time.sleep(max(0, self.LOOP_DURATION - (end - start)))

    def run(self):
        # get balance TODO: asyncronize
        self.exc1.update_balance()
        self.exc2.update_balance()

        # update status
        status = self.get_status()

        while True:
            start = time.time()

            # update tickers
            self.send_async_requests(self.update_tickers, (self.exc1, self.exc2))

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                self.wait_until_next_loop(start)
                continue

            margin = self.calc_margin()
            expectation = self.get_margin_expectation(margin)  # little ~ ultra
            if expectation == "little":
                self.wait_until_next_loop(start)
                continue

            approach = self.get_approach()  # level/tilt
            trans_size = self.get_size(expectation, status, approach)  # 0 ~ 13
            if trans_size == 0:
                self.wait_until_next_loop(start)
                continue

            # order TODO: asyncronize
            # self.high_ask_exc.post_order("SELL", trans_size)
            # self.low_ask_exc.post_order("BUY", trans_size)

            # get balance TODO: asyncronize
            self.exc1.update_balance()
            self.exc2.update_balance()

            # update status
            status = self.get_status()
            self.show_trans_result()
            self.wait_until_next_loop(start)
    
    def simulate(self):
        self.exc1.balance_yen = 250000
        self.exc1.balance_btc = 0.02
        self.exc2.balance_yen = 250000
        self.exc2.balance_btc = 0.02

        # update status
        status = self.get_status()

        while True:
            start = time.time()

            # update tickers
            self.send_async_requests(self.update_tickers, (self.exc1, self.exc2))

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                print(relation)
                self.wait_until_next_loop(start)
                continue

            margin = self.calc_margin()
            expectation = self.get_margin_expectation(margin)  # little ~ ultra
            if expectation == "little":
                print(expectation)
                self.wait_until_next_loop(start)
                continue

            approach = self.get_approach()  # level/tilt
            trans_size = self.get_size(expectation, status, approach)  # 0 ~ 13
            if trans_size == 0:
                print(trans_size)
                self.wait_until_next_loop(start)
                continue

            self.simulated_order(trans_size)

            # update status
            status = self.get_status()

            self.wait_until_next_loop(start)


if __name__ == "__main__":
    bf = BitFlyer()
    gc = GmoCoin()
    arbitrage = Arbitrage(bf, gc)
    arbitrage.simulate()
