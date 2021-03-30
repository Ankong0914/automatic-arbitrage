import time
from datetime import datetime
import requests
import json
import hmac
import hashlib

from exchanges.exchange import Exchange


class Liquid(Exchange):
    def __init__(self):
        super(Liquid, self).__init__()
        self.NAME = "Liquid"
        self.URL = "https://api.liquid.com"
        self.TICKER_EP = "/products/5"
        self.BALANCE_EP = ""
        self.ORDER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0

        # with open("exchanges/key_config.json", "r") as f:
        #     key_conf = json.load(f)
        # self.api_key = key_conf[self.NAME]["api_key"]
        # self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()

        self.bid = int(ticker["market_bid"])
        self.ask = int(ticker["market_ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]

    def make_headers(self, method, path, reqBody=None):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        if reqBody is not None:
            reqBody = json.dumps(reqBody)
        else:
            reqBody = ''
        text = timestamp + method + path + reqBody
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

    def update_balance(self):
        request_url = f'{self.URL}/private{self.BALANCE_EP}'
        headers = self.make_headers("GET", self.BALANCE_EP)
        response = requests.get(request_url, headers=headers)
        balance = response.json()["data"]
        
        for currency_data in balance:
            if currency_data["symbol"] == "JPY":
                self.balance_jpy = int(currency_data["amount"])
            elif currency_data["symbol"] == "BTC":
                self.balance_btc = float(currency_data["amount"])

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


