import logging

logging.basicConfig(level=logging.INFO)

class Exchange:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.NAME = name
        self.balance_btc = 0
        self.balance_jpy = 0
