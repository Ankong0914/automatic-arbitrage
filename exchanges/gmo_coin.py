import requests

from exchange import Exchange


class GmoCoin(Exchange):
    def __init__(self):
        super(GmoCoin, self).__init__()
        self.NAME = "GMO Coin"
        self.URL = "https://api.coin.z.com/public"
        self.TICKER_EP = "/v1/ticker"
        self.MIN_TRANS_UNIT = 0.0001
        self.REMITTANCE_FEE = 0

    def get_ticker(self, symbol="BTC"):
        request_url = f'{self.URL}{self.TICKER_EP}?symbol={symbol}'
        response = requests.get(request_url)
        ticker = response.json()["data"][0]
        return ticker

    def update_ticker(self):
        ticker = self.get_ticker()

        self.bid = int(ticker["bid"])
        self.ask = int(ticker["ask"])
        self.spread = self.ask - self.bid
        self.timestamp = ticker["timestamp"]
