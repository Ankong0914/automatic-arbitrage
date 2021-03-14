from exchanges.gmo_coin import GmoCoin
from datetime import datetime

gc = GmoCoin()

side = "BUY"
size = "0"

ticker1 = datetime.now()
print(f"get_ticker1: {ticker1}")
print(gc.get_ticker())
print("-----------------------------")
buy = datetime.now()
print(f"buy: {buy}")
# gc.post_order(side, size)
print("-----------------------------")
ticker2 = datetime.now()
print(f"get_ticker2: {ticker2}")
print(gc.get_ticker())
print("-----------------------------")
