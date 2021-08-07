import logging

from exchanges.utils import send_http_request

class BaseTransaction:
    def __init__(self, exchange):
        self.logger = logging.getLogger(exchange.NAME)
        self.exchange = exchange
        self.conf = exchange.api_conf["transaction"]
        self.exc_name = exchange.NAME
    
    def get_executions_list(self):
        conf = self.conf["executions"]
        url, method, path = conf["url"], conf["method"], conf["path"]
        headers = self.exchange.generate_headers(path, method=method)
        exec_list = send_http_request(url, headers=headers)
        print(exec_list)

    def get_execution(self, id):
        print("Not Supported")  # TODO: Raise
