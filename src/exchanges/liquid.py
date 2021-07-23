from datetime import datetime
import jwt

from exchanges.exchange import Exchange
from exchanges.base_ticker import BaseTicker


class Liquid(Exchange):
    def __init__(self):
        super(Liquid, self).__init__("Liquid")
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_CHARGE_RATE = 0
        self.TRANS_CHARGE_RATE = 0

        self.ticker = self.create_ticker()

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

    def update_balance(self, balance):
        for currency_data in balance:
            if currency_data["currency"] == "JPY":
                balance_jpy = float(currency_data["balance"])
            elif currency_data["currency"] == "BTC":
                balance_btc = float(currency_data["balance"])
        self.balance = {
            "JPY": balance_jpy,
            "BTC": balance_btc
        }
    
    def gen_order_body(self, side, size, order_type_key, price=None):
        body = {
            "order_type": self.api_conf["order"][order_type_key],
            "product_id": 5,
            "side": side,
            "quantity": str(size)
        }
        if order_type_key == "limit":
            body["price"] = str(price)
        return body

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

    class Ticker(BaseTicker):
        def __init__(self, liquid):
            super(Liquid.Ticker, self).__init__(liquid)
            