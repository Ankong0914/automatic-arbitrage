import pandas as pd
import time


class Arbitrage():
    def __init__(self, exc1, exc2):
        self.exc1 = exc1
        self.exc2 = exc2
        self.high_ask_exc = None
        self.low_ask_exc = None
        self.LOOP_DURATION = 1.0
        self.status = self.get_status()  # TODO: rename
        self.trans_size_table = pd.read_csv("data/transaction_size.csv")

    def get_status(self):
        RATIO_THRES = 2
        RATIO_THRES_HEAVY = 5

        ratio = self.exc1.balance_btc / self.exc2.balance_btc
        if ratio < RATIO_THRES and ratio > (1 / RATIO_THRES):
            status = "balanced"
        elif ratio < RATIO_THRES_HEAVY and ratio > (1 / RATIO_THRES_HEAVY):
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

    def get_margin_expectation(self):
        MARGIN_THRES = [1000, 5000, 10000, 15000]

        margin = self.high_ask_exc.bid - self.low_ask_exc.ask
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

    def get_size(self, trans_size_table, expectation, status, approach):
        trans_size = self.trans_size_table[
                        (self.trans_size_table["expectation"] == expectation) &
                        (self.trans_size_table["credit_status"] == status) &
                        (self.trans_size_table["approach"] == approach)
                    ]["credit_size"].values[0]
        return trans_size

    def wait_until_next_loop(self, start):
        end = time.time()
        time.sleep(max(0, self.LOOP_DURATION - (end - start)))

    def run(self):
        while True:
            start = time.time()

            # update ticker # TODO: asyncronize
            self.exc1.update_ticker()
            self.exc2.update_ticker()

            relation = self.get_relation()  # gap/intersection/inclusion
            if relation != "gap":
                self.wait_until_next_loop(start)
                continue

            expectation = self.get_margin_expectation()  # little ~ ultra
            if expectation == "little":
                self.wait_until_next_loop(start)
                continue

            approach = self.get_approach()  # level/tilt
            trans_size = self.get_size(expectation, self.status, approach)  # 0 ~ 13
            if trans_size == 0:
                self.wait_until_next_loop(start)
                continue

            # order TODO: asyncronize
            self.high_ask_exc.post_order("SELL", trans_size)
            self.low_ask_exc.post_order("BUY", trans_size)

            # get balance TODO: asyncronize
            self.exc1.update_balance()
            self.exc2.update_balance()

            # update status
            self.status = self.get_status()
            self.wait_until_next_loop(start)
