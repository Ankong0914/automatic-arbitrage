import time
from datetime import datetime

from exchanges.exchange import Exchange
from exchanges.ticker import BaseTicker
from exchanges.account import BaseAccount
from exchanges.order import BaseOrder
from exchanges.transaction import BaseTransaction


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__("GMOCoin")
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_CHARGE_RATE = 0
        self._trans_charge_rate = {
            "taker": 0.0005,
            "maker": -0.0001
        }

        self.ticker = self.create_ticker()
        self.account = self.create_account()
        self.transaction = self.create_transaction()
    
    def get_nonce_for_headers(self):
        nonce = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        return nonce

    def get_transactions_from_id(self, id):
        url = f"https://api.coin.z.com/private/v1/executions?orderId={id}"
        method, path = "GET", "/v1/executions"
        headers = self.generate_headers(path, method=method)
        transactions = send_http_request(url, headers=headers)
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
        def __init__(self, gmocoin):
            super(GmoCoin.Ticker, self).__init__(gmocoin)
        
        def parse(self, ticker_data):
            ticker_data = ticker_data["data"][0]
            self.ask = ticker_data[self.conf["ask_key"]]
            self.bid = ticker_data[self.conf["bid_key"]]
            self.high = ticker_data[self.conf["high_key"]]
            self.low = ticker_data[self.conf["low_key"]]
            self.volume = ticker_data[self.conf["volume_key"]]
            self.timestamp = ticker_data[self.conf["timestamp_key"]]
    

    class Account(BaseAccount):
        def __init__(self, gmocoin):
            super(GmoCoin.Account, self).__init__(gmocoin)

        def parse_balance(self, balance):
            for currency_data in balance["data"]:
                if currency_data["symbol"] == "JPY":
                    balance_jpy = float(currency_data["amount"])
                elif currency_data["symbol"] == "BTC":
                    balance_btc = float(currency_data["amount"])
            self.balance = {
                "JPY": balance_jpy,
                "BTC": balance_btc
            }
            self.logger.info("balance is updated")


    class Transaction(BaseTransaction):
        def __init__(self, gmocoin):
            super(GmoCoin.Transaction, self).__init__(gmocoin)
        
        def get_executions_list(self):
            print("Not Supported")  # TODO: Raise

     
    class Order(BaseOrder):
        def __init__(self, gmocoin, order_type_key, side_key, size, price=None):
            super(GmoCoin.Order, self).__init__(gmocoin, order_type_key, side_key, size, price)
        
        def generate_body(self):
            body = {
                "symbol": "BTC",
                "side": self.side,
                "executionType": self.order_type,
                "size": self.size
            }
            if self.order_type_key == "limit":
                body["price"] = str(int(self.price))
            return body