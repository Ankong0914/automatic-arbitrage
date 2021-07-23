import logging

from exchanges.utils import send_http_request


class BaseAccount:
    def __init__(self, exchange):
        self.logger = logging.getLogger(exchange.NAME)
        self.exchange = exchange
        self.conf = exchange.api_conf["balance"]
        self.exc_name = exchange.NAME
    
    def fetch_balance(self):
        url, method, path = self.conf["url"], self.conf["method"], self.conf["path"]
        headers = self.exchange.generate_headers(path, method=method)
        balance = send_http_request(url, headers=headers)
        self.parse_balance(balance)