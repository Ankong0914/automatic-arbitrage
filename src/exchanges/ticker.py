import os
import logging

from exchanges.utils import format_timestamp
from exchanges.utils import send_http_request


DB_API_PORT = os.environ.get("DB_API_PORT")

class Ticker:
    def __init__(self, exchange, ask, bid, high, low, volume, timestamp):
        self.logger = logging.getLogger(exchange.NAME)
        self.exchange = exchange
        self.conf = exchange.api_conf["ticker"]
        self.exc_name = exchange.NAME
        self.ask = ask
        self.bid = bid
        self.high = high
        self.low = low
        self.volume = volume
        self.timestamp = format_timestamp(timestamp)
        self._dict = {}

    
    def __str__(self):
        return str(self.dict)
    
    @property
    def dict(self):
        self._dict = {
            "exchange": self.exc_name,
            "ask": self.ask,
            "bid": self.bid,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "timestamp": self.timestamp
        }
        return self._dict

    def insert_db(self):
        url = f"http://db-api:{DB_API_PORT}/ticker"
        headers = {"Content-Type": "application/json"}
        response = send_http_request(url, headers=headers, body=self.dict)
        return response