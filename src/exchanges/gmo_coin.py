import time
from datetime import datetime
import logging

from exchanges.exchange import Exchange
from exchanges.base_ticker import BaseTicker


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__("GMOCoin")
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0.0005

        self.ticker = self.Ticker(self.api_conf["ticker"], self.NAME)

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
    
    def gen_order_body(self, side, size, order_type_key, price=None):
        body = {
            "symbol": "BTC",
            "side": side,
            "executionType": self.api_conf["order"][order_type_key],
            "size": size
        }
        if order_type_key == "limit":
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

    class Ticker(BaseTicker):
        def __init__(self, conf, name):
            super(GmoCoin.Ticker, self).__init__(conf, name)
            self.logger = logging.getLogger(name)
        
        def parse(self, ticker_data):
            ticker_data = ticker_data["data"][0]
            self.ask = ticker_data[self.conf["ask_key"]]
            self.bid = ticker_data[self.conf["bid_key"]]
            self.high = ticker_data[self.conf["high_key"]]
            self.low = ticker_data[self.conf["low_key"]]
            self.volume = ticker_data[self.conf["volume_key"]]
            self.timestamp = ticker_data[self.conf["timestamp_key"]]