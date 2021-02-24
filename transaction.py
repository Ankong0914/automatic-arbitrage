import csv
import pandas as pd
from itertools import combinations

from exchange import BitFlyer
from exchange import GmoCoin

bf = BitFlyer()
gc = GmoCoin()

def compare_price(tickers):
    for ticker_pair in combinations(tickers, 2):
        if ticker_pair[0].bid > ticker_pair[1].ask:
            sell_request(ticker_pair[0])
            buy_request(ticker_pair[1])
        elif ticker_pair[1].bid > ticker_pair[0].ask:
            sell_request(ticker_pair[1])
            buy_request(ticker_pair[0])
        else:
            pass


def buy(ticker, amount):
    if ticker.exchange == "bit_flyer":
        exc = bf
    elif ticker.exchange == "gmo_coin":
        exc = gc
    else:
        "ERROR"
    exc.balance_btc += amount
    exc.balance_jpy -= ticker.ask * amount


def sell(ticker, amount):
    if ticker.exchange == "bit_flyer":
        exc = bf
    elif ticker.exchange == "gmo_coin":
        exc = gc
    else:
        "ERROR"
    exc.balance_btc -= amount
    exc.balance_jpy += ticker.bid * amount


# TODO: async
def buy_request(ticker):
    # post
    amount = 0.001
    buy(ticker, amount)

    print(f"------------------------")
    print(f"Bitflyer  jpy: {bf.balance_jpy}, btc: {bf.balance_btc}")
    print(f"GMOCoin   jpy: {gc.balance_jpy}, btc: {gc.balance_btc}")
    print(f"PROFIT: {bf.balance_jpy + gc.balance_jpy - 400000}")


# TODO: async
def sell_request(ticker):
    # post
    amount = 0.001
    sell(ticker, amount)


# with open(""data/chart_bitflyer.csv, "r") as f_bf, open("data/chart_gmocoin.csv", "r") as f_gc:
#     chart_bf = csv.reader(f_bf)
#     chart_gc = csv.reader(f_gc)
#     for ticker_bf, ticker_gc in zip(chart_bf, chart_gc):
#         compare_price([ticker_bf, ticker_gc])


chart_bf = pd.read_csv("data/chart_bitflyer.csv")
chart_gc = pd.read_csv("data/chart_gmocoin.csv")

for ticker_bf, ticker_gc in zip(chart_bf.itertuples(), chart_gc.itertuples()):
    compare_price([ticker_bf, ticker_gc])

print(vars(bf))
print(vars(gc))
