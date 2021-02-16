import time
import requests


class Exchange:
    def __init__(self):
        pass


    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = int(ticker["bid"])
        self.ask = int(ticker["ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__()
        self.URL = "https://coincheck.com"
        self.TICKER_EP = "/api/ticker"
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_FEE = 0.001

    def get_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()
        return ticker


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.00000001
        self.REMITTANCE_FEE = 0.0004


class DmmBitcoin(Exchange):
    def __init__(self):
        super(DmmBitcoin, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__()
        self.URL = "https://api.coin.z.com/public"
        self.TICKER_EP = "/v1/ticker"
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0

    def get_ticker(self, symbol="BTC"):
        request_url = f'{self.URL}{self.TICKER_EP}?symbol={symbol}'
        response = requests.get(request_url)
        ticker = response.json()["data"][0]
        return ticker


class BitBank(Exchange):
    def __init__(self):
        super(BitBank, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0.001


class TaoTao(Exchange):
    def __init__(self):
        super(TaoTao, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0


class LiquidByQuoine(Exchange):
    def __init__(self):
        super(LiquidByQuoine, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0007


class SviVcTrade(Exchange):
    def __init__(self):
        super(SviVcTrade, self).__init__()
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0


def compare_price(exc1, exc2):
    exc1.update_ticker()
    exc2.update_ticker()

    if exc1.ask > exc2.ask:
        profit = exc1.bid - exc2.ask
    else:
        profit = exc2.bid - exc1.ask
    print(f"profit is {profit} yen.")

if __name__ == '__main__':
    cc = CoinCheck()
    gc = GmoCoin()
    compare_price(cc, gc)