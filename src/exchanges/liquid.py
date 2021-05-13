import time
from datetime import datetime
import requests
import json
import jwt

from exchanges.exchange import Exchange

class Liquid(Exchange):
    def __init__(self):
        super(Liquid, self).__init__("Liquid")
        self.URL = "https://api.liquid.com"
        self.TICKER_EP = "/products/5"
        self.BALANCE_EP = "/accounts/balance"
        self.ORDER_EP = "/orders/"
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self):
        try:
            url = f'{self.URL}{self.TICKER_EP}'
            response = requests.get(url)
            response.raise_for_status()
            ticker = response.json()

            self.bid = int(ticker["market_bid"])
            self.ask = int(ticker["market_ask"])
            self.timestamp = ticker["timestamp"]
            self.logger.info("ticker is updated")

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on updating ticker")
            raise

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
        try:
            url = f'{self.URL}{self.BALANCE_EP}'
            headers = self.make_headers(self.BALANCE_EP)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            balance = response.json()

            for currency_data in balance:
                if currency_data["currency"] == "JPY":
                    self.balance_jpy = int(float(currency_data["balance"]))
                elif currency_data["currency"] == "BTC":
                    self.balance_btc = float(currency_data["balance"])
            self.logger.info("balance is updated")

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on updating balance")
            raise

    def post_order(self, side, size):
        try:
            url = f'{self.URL}{self.ORDER_EP}'
            body = {
                "order": {
                    "order_type": "market",
                    "product_id": 5,
                    "side": side,
                    "quantity": str(size)
                }
            }
            headers = self.make_headers(self.ORDER_EP)
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            self.logger.info("order is successfully constracted")
            print(json.dumps(response.json()))
            
        except requests.exceptions.RequestException as e:
            self.logger.error("request error on posting an order")
            raise


