import time
import requests
from itertools import combinations


class Exchange:
    def __init__(self):
        pass


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__()
        self.NAME = "Coincheck"
        self.URL = "https://coincheck.com"
        self.TICKER_EP = "/api/ticker"
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_FEE = 0.001

    def get_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()
        return ticker

    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = ticker["bid"]
        self.ask = ticker["ask"]
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__()
        self.NAME = "bitFlyer"
        self.URL = "https://api.bitflyer.com"
        self.TICKER_EP = "/v1/ticker"
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004
        # TODO:
        self.balance_jpy = 200000
        self.balance_btc = 0.02
        self.credit = int(self.balance_btc / self.MIN_TRANS_UNIT)


    def get_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()
        return ticker

    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = ticker["best_bid"]
        self.ask = ticker["best_ask"]
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]


class DmmBitcoin(Exchange):
    def __init__(self):
        super(DmmBitcoin, self).__init__()
        self.NAME = "DMM Bitcoin"
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__()
        self.NAME = "GMO Coin"
        self.URL = "https://api.coin.z.com/public"
        self.TICKER_EP = "/v1/ticker"
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0
        # TODO:
        self.balance_jpy = 200000
        self.balance_btc = 0.02
        self.credit = int(self.balance_btc / self.MIN_TRANS_UNIT)

    def get_ticker(self, symbol="BTC"):
        request_url = f'{self.URL}{self.TICKER_EP}?symbol={symbol}'
        response = requests.get(request_url)
        ticker = response.json()["data"][0]
        return ticker

    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = int(ticker["bid"])
        self.ask = int(ticker["ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]


class BitBank(Exchange):
    def __init__(self):
        super(BitBank, self).__init__()
        self.NAME = "bitbank"
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0.001


class TaoTao(Exchange):
    def __init__(self):
        super(TaoTao, self).__init__()
        self.NAME = "TAOTAO"
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0


class LiquidByQuoine(Exchange):
    def __init__(self):
        super(LiquidByQuoine, self).__init__()
        self.NAME = "Liquid"
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0007


class SviVcTrade(Exchange):
    def __init__(self):
        super(SviVcTrade, self).__init__()
        self.NAME = "SVI VC Trade"
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0


# def compare_price(exc1, exc2):
#     exc1.update_ticker()
#     exc2.update_ticker()

#     if exc1.ask > exc2.ask:
#         profit = exc1.bid - exc2.ask
#     else:
#         profit = exc2.bid - exc1.ask
#     print(f"profit is {profit} yen.")

def compare_price(exchanges):
    for exchange in exchanges:
        exchange.update_ticker()

    for exc_pair in combinations(exchanges, 2):
        print(f"{exc_pair[0].NAME}で1 BTCを購入し、{exc_pair[1].NAME}で1 BTCを売却したときの利益")
        print(f"profit: ")


    if exc1.ask > exc2.ask:
        profit = exc1.bid - exc2.ask
    else:
        profit = exc2.bid - exc1.ask
    print(f"profit is {profit} yen.")

if __name__ == '__main__':
    bf = BitFlyer()
    gc = GmoCoin()
    while True:
        compare_price(bf, gc)