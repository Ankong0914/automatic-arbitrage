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
        self.TRANS_EP = "/executions/me"
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

    def generate_headers(self, path):
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
            headers = self.generate_headers(self.BALANCE_EP)
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

    def get_transactions(self):
        try:
            url = f'{self.URL}{self.TRANS_EP}?product_id=5'
            headers = self.generate_headers(f"{self.TRANS_EP}?product_id=5")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.logger.info("transactions are collectly got")
            transactions = response.json()["models"]
            return transactions

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on getting transactions")
            raise

    def get_transactions_from_id(self, id):
        all_transactions = self.get_transactions()
        transactions = [transaction for transaction in all_transactions if transaction["order_id"] == id]
        return transactions

    def pick_transactions_info(self, transactions):
        trans_result = []
        for transaction  in transactions:
            trans_info = {
                "id": transaction["id"],
                "timestamp": transaction["timestamp"],
                "side": transaction["my_side"],
                "size": float(transaction["quantity"]),
                "price": float(transaction["price"])
            }
            trans_result.append(trans_info)
        return trans_result

    def send_order(self, side, size):
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
            headers = self.generate_headers(self.ORDER_EP)
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            self.logger.info("order is successfully constracted")

            order_id = response.json()["id"]
    
        except requests.exceptions.RequestException as e:
            self.logger.error("request error on posting an order")
            raise

        else:
            self.update_balance()
            transaction = self.get_transactions_from_id(order_id)
            trans_result = self.pick_transactions_info(transactions)
            return trans_result

    def send_buy_order(self, size):
        side = "buy"
        trans_result = self.send_order(side, size)

    def send_sell_order(self, size):
        side = "sell"
        trans_result = self.send_order(side, size)
