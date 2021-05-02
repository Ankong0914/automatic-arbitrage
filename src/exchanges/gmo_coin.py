import time
from datetime import datetime
import requests
import json
import hmac
import hashlib

from exchanges.exchange import Exchange


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__("GMO Coin")
        self.URL = "https://api.coin.z.com"
        self.TICKER_EP = "/v1/ticker"
        self.BALANCE_EP = "/v1/account/assets"
        self.ORDER_EP = "/v1/order"
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0.0005

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self, symbol="BTC"):
        try:
            url = f'{self.URL}/public{self.TICKER_EP}?symbol={symbol}'
            response = requests.get(url)
            response.raise_for_status()
            ticker = response.json()["data"][0]

            self.bid = int(ticker["bid"])
            self.ask = int(ticker["ask"])
            self.timestamp = ticker["timestamp"]
            self.logger.info("ticker is updated")

        except requests.exceptions.RequestException as e:
            self.logger.warning("request error on updating ticker")
            raise

    def make_headers(self, method, path, body=None):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        if body is not None:
            body = json.dumps(body)
        else:
            body = ''
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

    def update_balance(self):
        try:
            url = f'{self.URL}/private{self.BALANCE_EP}'
            headers = self.make_headers("GET", self.BALANCE_EP)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            balance = response.json()["data"]
            
            for currency_data in balance:
                if currency_data["symbol"] == "JPY":
                    self.balance_jpy = int(currency_data["amount"])
                elif currency_data["symbol"] == "BTC":
                    self.balance_btc = float(currency_data["amount"])
            self.logger.info("balance is updated")

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on updating balance")
            raise

    def post_order(self, side, size):
        try:
            url = f'{self.URL}/private{self.ORDER_EP}'
            body = {
                "symbol": "BTC",
                "side": side,
                "executionType": "MARKET",
                "size": size
            }
            headers = self.make_headers("POST", self.ORDER_EP, body)
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            print(json.dumps(response.json(), indent=2))
        
        except requests.exceptions.RequestException as e:
            self.logger.error("request error on posting an order")
            raise

if __name__ == "__main__":
    gc = GmoCoin()

