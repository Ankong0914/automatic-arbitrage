import time
from datetime import datetime
import requests
import json
import hmac
import hashlib

from exchanges.exchange import Exchange


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__()
        self.NAME = "Coincheck"
        self.URL = "https://coincheck.com"
        self.TICKER_EP = "/api/ticker"
        self.BALANCE_EP = "/api/accounts/balance"
        self.ORDER_EP = ""
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_CHARGE_RATE = 0.001
        self.TRANS_CHARGE_RATE = 0

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()

        self.bid = int(ticker["bid"])
        self.ask = int(ticker["ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]

    def make_headers(self, path, reqBody=None):
        timestamp = str(int(time.time()))
        if reqBody is not None:
            reqBody = json.dumps(reqBody)
        else:
            reqBody = ''
        text = timestamp + path + reqBody
        sign = hmac.new(
            bytes(self.api_secret.encode('ascii')),
            bytes(text.encode('ascii')),
            hashlib.sha256
            ).hexdigest()
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-NONCE': timestamp,
            'ACCESS-SIGNATURE': sign,
            'Content-Type': 'application/json'
        }
        return headers

    def update_balance(self):
        request_url = f'{self.URL}{self.BALANCE_EP}'
        headers = self.make_headers(request_url)
        response = requests.get(request_url, headers=headers)
        balance = response.json()

        self.balance_jpy = int(balance["jpy"])
        self.balance_btc = float(balance["btc"])

    def post_order(self, side, size):
        request_url = f'{self.URL}/private{self.ORDER_EP}'
        reqBody = {
            "symbol": "BTC",
            "side": side,
            "executionType": "MARKET",
            "size": size
        }
        headers = self.make_headers("POST", self.ORDER_EP, reqBody)
        response = requests.post(request_url, headers=headers, data=json.dumps(reqBody))
        print(json.dumps(response.json(), indent=2))


