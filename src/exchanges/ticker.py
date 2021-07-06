import os

from exchanges.utils import format_timestamp
from exchanges.utils import send_http_request


DB_API_PORT = os.environ["DB_API_PORT"]

class Ticker:
    def __init__(self, exc_name="AnyExchange"):
        self.exchange = exc_name
        self._ask = 0.0
        self._bid = 0.0
        self._high = 0.0
        self._low = 0.0
        self._volume = 0.0
        self._timestamp = "1970-01-01T09:00:00+09:00"
        self._dict = {}
    
    def __str__(self):
        return str(self.dict)
    
    @property
    def ask(self):
        return self._ask

    @ask.setter
    def ask(self, value):
        self._ask = float(value)
    
    @property
    def bid(self):
        return self._bid

    @bid.setter
    def bid(self, value):
        self._bid = float(value)
    
    @property
    def high(self):
        return self._high

    @high.setter
    def high(self, value):
        self._high = float(value)
    
    @property
    def low(self):
        return self._low

    @low.setter
    def low(self, value):
        self._low = float(value)
    
    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = float(value)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = format_timestamp(value)
    
    @property
    def dict(self):
        self._dict = {
            "exchange": self.exchange,
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