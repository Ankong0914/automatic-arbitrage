import time

from exchanges.exchange import Exchange
from exchanges.ticker import BaseTicker
from exchanges.account import BaseAccount
from exchanges.order import BaseOrder


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__("bitFlyer")
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004
        # TODO: this value is changed depends on the amount of transaction for recent month
        self.TRANS_CHARGE_RATE = 0.0015

        self.ticker = self.create_ticker()
        self.account = self.create_account()

    def get_nonce_for_headers(self):
        nonce = str(time.time())
        return nonce


    class Ticker(BaseTicker):
        def __init__(self, bitflyer):
            super(BitFlyer.Ticker, self).__init__(bitflyer)
        
        def parse(self, ticker_data):
            self.ask = ticker_data[self.conf["ask_key"]]
            self.bid = ticker_data[self.conf["bid_key"]]
            self.volume = ticker_data[self.conf["volume_key"]]
            self.timestamp = ticker_data[self.conf["timestamp_key"]]
    

    class Account(BaseAccount):
        def __init__(self, bitflyer):
            super(BitFlyer.Account, self).__init__(bitflyer)

        def parse_balance(self, balance):
            for currency_data in balance:
                if currency_data["currency_code"] == "JPY":
                    balance_jpy = currency_data["amount"]
                elif currency_data["currency_code"] == "BTC":
                    balance_btc = currency_data["amount"]
            self.balance = {
                "JPY": balance_jpy,
                "BTC": balance_btc
            }
            self.logger.info("balance is updated")

    
    class Order(BaseOrder):
        def __init__(self, bitflyer, order_type_key, side_key, size, price=None):
            super(BitFlyer.Order, self).__init__(bitflyer, order_type_key, side_key, size, price)