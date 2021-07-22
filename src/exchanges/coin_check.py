import time
import logging

from exchanges.exchange import Exchange
from exchanges.base_ticker import BaseTicker


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__("Coincheck")
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_CHARGE_RATE = 0.001
        self.TRANS_CHARGE_RATE = 0
        
        self.ticker = self.Ticker(self.api_conf["ticker"], self.NAME)
        self.nonce = "0"

    def update_balance(self, balance):
        self.balance = {
            "JPY": float(balance["jpy"]),
            "BTC": float(balance["btc"])
        }

    def get_nonce_for_headers(self):
        pre_nonce = self.nonce
        self.nonce = str(int(time.time()))
        if self.nonce <= pre_nonce:
            self.nonce = str(int(pre_nonce) + 1)
        return self.nonce
    
    def gen_order_body(self, side, size):
        if side == "market_buy":
            self.fetch_ticker()
            size_jpy = size * self.ticker["ask"]
            body = {
                "pair": "btc_jpy",
                "order_type": side,
                "market_buy_amount": size_jpy
            }
        elif side == "market_sell":
            body = {
                "pair": "btc_jpy",
                "order_type": side,
                "amount": size,
            }
        else:
            self.logger.error("unexpected side is set")
        return body
    
    def get_transactions_from_id(self, id):
        all_transactions = self.get_transactions()["transactions"]
        transactions = [transaction for transaction in all_transactions if transaction["order_id"] == id]
        return transactions
    
    def pick_transactions_info(self, transactions):
        if len(transactions) == 0:
            self.logger.info("this transaction doesn't exist or hasn't constracted yet.")
        
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
    
    class Ticker(BaseTicker):
        def __init__(self, conf, name):
            super(CoinCheck.Ticker, self).__init__(conf, name)
            self.logger = logging.getLogger(name)
        