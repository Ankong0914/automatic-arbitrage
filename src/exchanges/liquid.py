import time
from datetime import datetime
import requests
import json
import jwt

from exchanges.exchange import Exchange


class Liquid(Exchange):
    def __init__(self):
        super(Liquid, self).__init__()
        self.NAME = "Liquid"
        self.URL = "https://api.liquid.com"
        self.TICKER_EP = "/products/5"
        self.BALANCE_EP = "/accounts/balance"
        self.ORDER_EP = ""
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self):
        request_url = f'{self.URL}{self.TICKER_EP}'
        response = requests.get(request_url)
        ticker = response.json()

        self.bid = int(ticker["market_bid"])
        self.ask = int(ticker["market_ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]

    def make_headers(self, path):
        timestamp = datetime.now().timestamp()
        payload = {
            "path": path,
            "nonce": timestamp,
            "token_id": self.api_key
        }
        signature = jwt.encode(payload, self.api_secret, algorithm='HS256')

        headers = {
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': signature,
            'Content-Type' : 'application/json'
        }
        return headers

    def update_balance(self):
        request_url = f'{self.URL}{self.BALANCE_EP}'
        headers = self.make_headers(self.BALANCE_EP)
        response = requests.get(request_url, headers=headers)
        balance = response.json()

        for currency_data in balance:
            if currency_data["currency"] == "JPY":
                self.balance_jpy = int(float(currency_data["balance"]))
            elif currency_data["currency"] == "BTC":
                self.balance_btc = float(currency_data["balance"])

    # def post_order(self, side, size):
    #     request_url = f'{self.URL}/private{self.ORDER_EP}'
    #     reqBody = {
    #         "symbol": "BTC",
    #         "side": side,
    #         "executionType": "MARKET",
    #         "size": size
    #     }
    #     headers = self.make_headers("POST", self.ORDER_EP, reqBody)
    #     response = requests.post(request_url, headers=headers, data=json.dumps(reqBody))
    #     print(json.dumps(response.json(), indent=2))


