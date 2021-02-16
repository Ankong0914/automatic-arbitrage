import time
import requests


class Exchange:
    def __init__(self):
        pass
    
    def get_ticker(self):
        response = requests.get(f'{self.URL}{self.TICKER_EP}')
        ticker = response.json()
        self.bid = ticker["bid"]  # selling price 
        self.ask = ticker["ask"]  # buying price
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__()
        self.URL = "https://coincheck.com"
        self.TICKER_EP = "/api/ticker"
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_FEE = 0.001


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
        self.URL = ""
        self.TICKER_EP = ""
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0


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


if __name__ == '__main__':
    cc = CoinCheck()
    cc.get_ticker()
    print(cc.bid, cc.ask, cc.spread, cc.timestamp)