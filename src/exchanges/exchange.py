import os
import logging
import json
import hmac
import hashlib

from exchanges.utils import send_http_request

logging.basicConfig(level=logging.WARNING)

DB_API_PORT = os.environ.get("DB_API_PORT")

class Exchange:
    def __init__(self, name):
        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[name]["api_key"]
        self.api_secret = key_conf[name]["api_secret"]

        with open("exchanges/api_config.json", "r") as f:
            api_configs = json.load(f)
        self.api_conf = api_configs[name]

        self.logger = logging.getLogger(name)
        self.NAME = name
        self.order_type = "limit"
    
    @property
    def trans_charge_rate(self):
        if self.order_type == "market":
            return self._trans_charge_rate["taker"]
        elif self.order_type == "limit":
            return self._trans_charge_rate["maker"]

    def create_ticker(self):
        return self.Ticker(self)

    def create_account(self):
        return self.Account(self)
    
    def create_transaction(self):
        return self.Transaction(self)
    
    def create_order(self, order_type_key, side_key, size, price=None):
        return self.Order(self, order_type_key, side_key, size, price)

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

    def pick_order_id(self, order_result):
        pass

    def get_transaction_result(self, order_id):
        transactions = self.get_transactions_from_id(order_id)
        trans_result = self.pick_transactions_info(transactions)
        return trans_result
