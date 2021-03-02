import time
import requests
import json
import time
import hmac
import hashlib
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
        self.BALANCE_EP = "/v1/me/getbalance"
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004

        with open("key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

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
    
    def make_headers(self, method, path, body=""):
        timestamp = str(time.time())
        text = timestamp + method + path + body
        sign = hmac.new( bytes( self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        return headers

    def get_balance(self):
        request_url = f'{self.URL}{self.BALANCE_EP}'
        headers = self.make_headers("GET", self.BALANCE_EP)
        response = requests.get(request_url, headers=headers)
        balance = response.json()
        return balance


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


if __name__ == '__main__':
    bf = BitFlyer()
    gc = GmoCoin()
    
    print(bf.get_balance())