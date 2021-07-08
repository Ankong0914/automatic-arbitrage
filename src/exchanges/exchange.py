import os
import logging
import json
import requests
from  datetime import datetime
import pytz
import re
import time
import hmac
import hashlib

from exchanges.ticker import Ticker
from exchanges.utils import send_http_request

logging.basicConfig(level=logging.INFO)

DB_API_PORT = os.environ.get("DB_API_PORT")

class Exchange:
    jst = pytz.timezone("Asia/Tokyo")

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.NAME = name
        self.ticker = Ticker()

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

        with open("exchanges/api_config.json", "r") as f:
            api_configs = json.load(f)
        self.api_conf = api_configs[self.NAME]

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

    def update_ticker(self, ticker_data):
        conf = self.api_conf["ticker"]
        self.ticker.ask = ticker_data[conf["ask_key"]]
        self.ticker.bid = ticker_data[conf["bid_key"]]
        self.ticker.high = ticker_data[conf["high_key"]]
        self.ticker.low = ticker_data[conf["low_key"]]
        self.ticker.volume = ticker_data[conf["volume_key"]]
        self.ticker.timestamp = ticker_data[conf["timestamp_key"]]
    
    def fetch_ticker(self):
        conf = self.api_conf["ticker"]
        url = conf["url"]
        ticker_data = send_http_request(url)
        self.update_ticker(ticker_data)

    def update_balance(self, balance):
        pass

    def fetch_balance(self):
        conf = self.api_conf["balance"]
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.generate_headers(path, method=method)
        balance = send_http_request(url, headers=headers)
        self.update_balance(balance)
    
    def get_transactions(self):
        conf = self.api_conf["transactions"]
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.generate_headers(path, method=method)
        transactions = send_http_request(url, headers=headers)
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
        result = send_http_request(url, headers=headers, body=body) 

        order_id = result[conf["order_id_key"]]
        return order_id

    def get_transaction_result(self, order_id):
        transactions = self.get_transactions_from_id(order_id)
        trans_result = self.pick_transactions_info(transactions)
        return trans_result
