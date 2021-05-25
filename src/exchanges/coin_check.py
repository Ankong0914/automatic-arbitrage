import time
from datetime import datetime
import requests
import json
import hmac
import hashlib

from exchanges.exchange import Exchange


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__("Coincheck")
        self.URL = "https://coincheck.com"
        self.TICKER_EP = "/api/ticker"
        self.BALANCE_EP = "/api/accounts/balance"
        self.ORDER_EP = "/api/exchange/orders"
        self.TRANS_EP = "/api/exchange/orders/transactions"
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_CHARGE_RATE = 0.001
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

            self.bid = int(ticker["bid"])
            self.ask = int(ticker["ask"])
            self.timestamp = ticker["timestamp"]
            self.logger.info("ticker is updated")

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on updating ticker")
            raise

    def generate_headers(self, url, body=None):
        timestamp = str(int(time.time()))
        if body is not None:
            body = json.dumps(body)
        else:
            body = ''
        text = timestamp + url + body
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
        try:
            url = f'{self.URL}{self.BALANCE_EP}'
            headers = self.generate_headers(url)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            balance = response.json()

            self.balance_jpy = float(balance["jpy"])
            self.balance_btc = float(balance["btc"])
            self.logger.info("balance is updated")

        except requests.exceptions.RequestException as e:
            self.logger.error("request error on updating balance")
            raise
    
    def get_transactions(self):
        try:
            url = f'{self.URL}{self.TRANS_EP}'
            headers = self.generate_headers(url)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.logger.info("transactions are collectly got")
            transactions = response.json()["transactions"]
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
                "timestamp": transaction["created_at"],
                "side": transaction["side"],
                "size": abs(float(transaction["funds"]["btc"])),
                "price": float(transaction["rate"])
            }
            trans_result.append(trans_info)
        return trans_result

    def send_order(self, side, size):
        try:
            url = f'{self.URL}{self.ORDER_EP}'
            body = {
                "pair": "btc_jpy",
                "order_type": side,
                "market_buy_amount": size,
            }
            headers = self.generate_headers(url, body)
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
        side = "market_buy"
        size_jpy = size * self.ask  # Coincheck api allows size of jpy only 
        trans_result = self.send_order(side, size_jpy)

    def send_sell_order(self, size):
        side = "market_sell"
        size_jpy = size * self.bid  # Coincheck api allows size of jpy only 
        trans_result = self.send_order(side, size_jpy)
        