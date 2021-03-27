import time
import requests
import json
import hmac
import hashlib

from exchanges.exchange import Exchange


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__()
        self.NAME = "bitFlyer"
        self.URL = "https://api.bitflyer.com"
        self.TICKER_EP = "/v1/ticker"
        self.BALANCE_EP = "/v1/me/getbalance"
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004
        # TODO: this value is changed depends on the amount of transaction for recent month
        self.TRANS_CHARGE_RATE = 0.0015

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()

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

    def update_balance(self):
        request_url = f'{self.URL}{self.BALANCE_EP}'
        headers = self.make_headers("GET", self.BALANCE_EP)
        response = requests.get(request_url, headers=headers)
        balance = response.json()

        for currency_data in balance:
            if currency_data["currency_code"] == "JPY":
                self.balance_jpy = int(currency_data["amount"])
            elif currency_data["currency_code"] == "BTC":
                self.balance_btc = currency_data["amount"]
