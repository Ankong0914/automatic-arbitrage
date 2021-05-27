from exchanges.exchange import Exchange


class CoinCheck(Exchange):
    def __init__(self):
        super(CoinCheck, self).__init__("Coincheck")
        self.MIN_TRANS_UNIT = 0.005
        self.REMITTANCE_CHARGE_RATE = 0.001
        self.TRANS_CHARGE_RATE = 0

    def update_balance(self, balance):
        self.balance = {
            "JPY": float(balance["jpy"]),
            "BTC": float(balance["btc"])
        }
    
    def gen_order_body(self, side, size):
        if side == "market_buy":
            size_jpy = size * self.ticker["ask"]
        elif side == "market_sell"
            size_jpy = size * self.ticker["bid"]
        else:
            self.logger.error("unexpected side is set")

        body = {
            "pair": "btc_jpy",
            "order_type": side,
            "market_buy_amount": size_jpy,
        }
        return body
    
    def get_transactions_from_id(self, id):
        all_transactions = self.get_transactions()["transactions"]
        transactions = [transaction for transaction in all_transactions if transaction["order_id"] == id]
        return transactions
    
    def pick_transactions_info(self, transactions):
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

        