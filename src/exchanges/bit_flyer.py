import time
import logging

from exchanges.exchange import Exchange
from exchanges.base_ticker import BaseTicker


class BitFlyer(Exchange):
    def __init__(self):
        super(BitFlyer, self).__init__("bitFlyer")
        self.MIN_TRANS_UNIT = 0.001
        self.REMITTANCE_FEE = 0.0004
        # TODO: this value is changed depends on the amount of transaction for recent month
        self.TRANS_CHARGE_RATE = 0.0015

        self.ticker = self.Ticker(self.api_conf["ticker"], self.NAME)

    def get_nonce_for_headers(self):
        nonce = str(time.time())
        return nonce

    def update_balance(self, balance):
        for currency_data in balance:
            if currency_data["currency_code"] == "JPY":
                self.balance_jpy = int(currency_data["amount"])
            elif currency_data["currency_code"] == "BTC":
                self.balance_btc = currency_data["amount"]
        self.logger.info("balance is updated")

    class Ticker(BaseTicker):
        def __init__(self, conf, name):
            super(BitFlyer.Ticker, self).__init__(conf, name)
            self.logger = logging.getLogger(name)
        
        def parse(self, ticker_data):
            self.ask = ticker_data[self.conf["ask_key"]]
            self.bid = ticker_data[self.conf["bid_key"]]
            self.volume = ticker_data[self.conf["volume_key"]]
            self.timestamp = ticker_data[self.conf["timestamp_key"]]