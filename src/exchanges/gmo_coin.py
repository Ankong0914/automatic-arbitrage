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
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0.0005

        with open("exchanges/key_config.json", "r") as f:
            key_conf = json.load(f)
        self.api_key = key_conf[self.NAME]["api_key"]
        self.api_secret = key_conf[self.NAME]["api_secret"]

    def update_ticker(self, ticker_data):
        conf = self.api_conf["ticker"]
        ticker_data = ticker_data["data"][0]
        self.ticker.ask = ticker_data[conf["ask_key"]]
        self.ticker.bid = ticker_data[conf["bid_key"]]
        self.ticker.high = ticker_data[conf["high_key"]]
        self.ticker.low = ticker_data[conf["low_key"]]
        self.ticker.volume = ticker_data[conf["volume_key"]]
        self.ticker.timestamp = ticker_data[conf["timestamp_key"]]

    def update_balance(self, balance):
        for currency_data in balance["data"]:
            if currency_data["symbol"] == "JPY":
                balance_jpy = int(currency_data["amount"])
            elif currency_data["symbol"] == "BTC":
                balance_btc = float(currency_data["amount"])
        self.balance = {
            "JPY": balance_jpy,
            "BTC": balance_btc
        }
    
    def get_nonce_for_headers(self):
        nonce = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        return nonce
    
    def gen_order_body(self, side, size, order_type, price=None):
        body = {
            "symbol": "BTC",
            "side": side,
            "executionType": order_type,
            "size": size
        }
        if order_type == self.api_conf["order"]["limit"]:
            body["price"] = str(int(price))
        return body

    def get_transactions_from_id(self, id):
        url = f"https://api.coin.z.com/private/v1/executions?orderId={id}"
        method, path = "GET", "/v1/executions"
        headers = self.generate_headers(path, method=method)
        transactions = self.request_api(url, headers=headers)
        return transactions["data"]["list"]
    
    def pick_transactions_info(self, transactions):
        if len(transactions) == 0:
            self.logger.info("this transaction doesn't exist or hasn't constracted yet.")
        
        trans_result = []
        for transaction  in transactions:
            trans_info = {
                "id": transaction["executionId"],
                "timestamp": transaction["timestamp"],
                "side": transaction["side"],
                "size": float(transaction["size"]),
                "price": float(transaction["price"])
            }
            trans_result.append(trans_info)
        return trans_result
