from exchanges.utils import send_http_request


class BaseOrder:
    def __init__(self, exchange, order_type_key, side_key, price=None):
        self.exchange = exchange
        self.conf = exchange.api_conf["order"]
        self.exc_name = exchange.NAME
        self.order_type_key = order_type_key
        self.order_type = self.conf[order_type_key]
        self.side_key = side_key
        self.side = self.conf[side_key]
        self.price = price
    
    def send(self):
        body = self.generate_body()
        url, method, path = self.conf["url"], self.conf["method"], self.conf["path"]
        headers = self.exchange.generate_headers(path, method=method, body=body)
        result = send_http_request(url, headers=headers, body=body) 

        order_id = result[self.conf["order_id_key"]]
        return order_id
