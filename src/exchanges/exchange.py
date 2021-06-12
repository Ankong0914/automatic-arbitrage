import logging
import json
import requests
import time
import hmac
import hashlib

logging.basicConfig(level=logging.INFO)

class Exchange:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.NAME = name

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

        with open("exchanges/api_config.json", "r") as f:
            api_configs = json.load(f)
        self.api_conf = api_configs[self.NAME]

    def request_api(self, url, headers=None, body=None):
        if body is None:  # GET request
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                self.logger.error("request error on updating balance") # TODO
                raise
        else:  # POST request
            try:
                response = requests.post(url, headers=headers, data=json.dumps(body))
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                self.logger.error("request error on updating balance") # TODO
                raise

    def generate_headers(self, path, method="", body=""):
        conf = self.api_conf["auth"]
        nonce = self.get_nonce_for_headers()
        if body:
            body = json.dumps(body)
        text = nonce + method + path + body
        sign = hmac.new(
            bytes(self.api_secret.encode('ascii')),
            bytes(text.encode('ascii')),
            hashlib.sha256
            ).hexdigest()
        headers = {
            conf["access_key_key"]: self.api_key,
            conf["access_timestamp_key"]: nonce,
            conf["access_sign_key"]: sign,
            'Content-Type': 'application/json'
        }
        return headers

    def update_ticker(self, ticker):
        conf = self.api_conf["ticker"]
        self.ticker = {
            "ask": float(ticker[conf["ask_key"]]),
            "bid": float(ticker[conf["bid_key"]]),
            "timestamp": ticker[conf["timestamp_key"]]
        }
    
    def fetch_ticker(self):
        conf = self.api_conf["ticker"]
        url = conf["url"]
        ticker = self.request_api(url)
        self.update_ticker(ticker)

    def update_balance(self, balance):
        pass

    def fetch_balance(self):
        conf = self.api_conf["balance"]
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.generate_headers(path, method=method)
        balance = self.request_api(url, headers=headers)
        self.update_balance(balance)
    
    def get_transactions(self):
        conf = self.api_conf["transactions"]
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.generate_headers(path, method=method)
        transactions = self.request_api(url, headers=headers)
        return transactions

    def gen_order_body(self, side, size):
        pass

    def pick_order_id(self, order_result):
        pass
    
    def send_order(self, side_key, size, order_type_key="market", price=None):
        conf = self.api_conf["order"]
        side = conf[side_key]
        order_type = conf[order_type_key]
        body = self.gen_order_body(side, size, order_type, price=price)
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.generate_headers(path, method=method, body=body)
        result = self.request_api(url, headers=headers, body=body) 

        order_id = result[conf["order_id_key"]]
        return order_id

    def get_transaction_result(self, order_id):
        transactions = self.get_transactions_from_id(order_id)
        trans_result = self.pick_transactions_info(transactions)
        return trans_result
