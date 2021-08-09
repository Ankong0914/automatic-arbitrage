from datetime import datetime
import jwt

from exchanges.exchange import Exchange
from exchanges.account import BaseAccount
from exchanges.order import BaseOrder
from exchanges.transaction import BaseTransaction


class Liquid(Exchange):
    def __init__(self):
        super(Liquid, self).__init__("Liquid")
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_CHARGE_RATE = 0
        self._trans_charge_rate = {
            "taker": 0,
            "maker": 0
        }

        self.account = self.create_account()
        self.transaction = self.create_transaction()

    def generate_headers(self, path, method="", body=""):
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
    
    
    def parse_ticker(self, ticker_data):
        conf = self.api_conf["ticker"]
        parsed_ticker = {
            "ask": ticker_data[conf["ask_key"]],
            "bid": ticker_data[conf["bid_key"]],
            "high": float(ticker_data[conf["high_key"]]),
            "low": float(ticker_data[conf["low_key"]]),
            "volume": float(ticker_data[conf["volume_key"]]),
            "timestamp": ticker_data[conf["timestamp_key"]],
        }
        return parsed_ticker
        

    def get_transactions_from_id(self, id):
        all_transactions = self.get_transactions()["models"]
        transactions = [transaction for transaction in all_transactions if transaction["order_id"] == id]
        return transactions

    def pick_transactions_info(self, transactions):
        if len(transactions) == 0:
            self.logger.info("this transaction doesn't exist or hasn't constracted yet.")
        
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
    

    class Account(BaseAccount):
        def __init__(self, liquid):
            super(Liquid.Account, self).__init__(liquid)

        def parse_balance(self, balance):
            for currency_data in balance:
                if currency_data["currency"] == "JPY":
                    balance_jpy = float(currency_data["balance"])
                elif currency_data["currency"] == "BTC":
                    balance_btc = float(currency_data["balance"])
            self.balance = {
                "JPY": balance_jpy,
                "BTC": balance_btc
            }
            self.logger.info("balance is updated")
    

    class Transaction(BaseTransaction):
        def __init__(self, liquid):
            super(Liquid.Transaction, self).__init__(liquid)


    class Order(BaseOrder):
        def __init__(self, liquid, order_type_key, side_key, size, price=None):
            super(Liquid.Order, self).__init__(liquid, order_type_key, side_key, size, price)
        
        def generate_body(self):
            body = {
                "order_type": self.order_type,
                "product_id": 5,
                "side": self.side,
                "quantity": str(self.size)
            }
            if self.order_type_key == "limit":
                body["price"] = str(self.price)
            return body
            