import time
from datetime import datetime
import requests
import json
import hmac
import hashlib

from exchange import Exchange


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__()
        self.NAME = "GMO Coin"
        self.URL = "https://api.coin.z.com"
        self.TICKER_EP = "/v1/ticker"
        self.BALANCE_EP = "/v1/account/assets"
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0

        with open("../key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def get_ticker(self, symbol="BTC"):
        request_url = f'{self.URL}/public{self.TICKER_EP}?symbol={symbol}'
        response = requests.get(request_url)
        ticker = response.json()["data"][0]
        return ticker

    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = int(ticker["bid"])
        self.ask = int(ticker["ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]

    def make_headers(self, method, path, body=""):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        text = timestamp + method + path + body
        sign = hmac.new(
            bytes(self.api_secret.encode('ascii')),
            bytes(text.encode('ascii')),
            hashlib.sha256
            ).hexdigest()
        headers = {
            'API-KEY': self.api_key,
            'API-TIMESTAMP': timestamp,
            'API-SIGN': sign
        }
        return headers

    def get_balance(self):
        request_url = f'{self.URL}/private{self.BALANCE_EP}'
        print(request_url)
        headers = self.make_headers("GET", self.BALANCE_EP)
        response = requests.get(request_url, headers=headers)
        balance = response.json()
        return balance


if __name__ == "__main__":
    gc = GmoCoin()
    print(gc.get_balance())
