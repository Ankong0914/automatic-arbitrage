import time
import requests
import json
import hmac
import hashlib

from exchange import Exchange


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__()
        self.NAME = "bitFlyer"
        self.URL = "https://api.bitflyer.com"
        self.TICKER_EP = "/v1/ticker"
        self.BALANCE_EP = "/v1/me/getbalance"
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004

        with open("../key_config.json", "r") as f:
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
        sign = hmac.new(
            bytes(self.api_secret.encode('ascii')),
            bytes(text.encode('ascii')),
            hashlib.sha256
            ).hexdigest()
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
