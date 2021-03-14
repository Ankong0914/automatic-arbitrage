import csv
import pandas as pd
from itertools import combinations

from exchange import BitFlyer
from exchange import GmoCoin


def compare_prices(tickers):
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


def get_margin_expectation(high_ask_exc, low_ask_exc):
    MARGIN_THRES = [1000, 5000, 10000, 15000]

    margin = high_ask_exc.bid - low_ask_exc.ask
    if margin < MARGIN_THRES[0]:
        expectation = "little"
    elif margin < MARGIN_THRES[1]:
        expectation = "low"
    elif margin < MARGIN_THRES[2]:
        expectation = "mid"
    elif margin < MARGIN_THRES[3]:
        expectation = "high"
    else:
        expectation = "ultra"
    return expectation 


def get_relation(exc1, exc2):
    if exc1.ask > exc2.ask:
        high_ask_exc, low_ask_exc = exc1, exc2
        if exc1.bid > exc2.ask:
            relation = "gap"
        elif exc1.bid >= exc2.bid:
            relation = "intersection"
        else:
            relation = "inclusion"
    else:
        high_ask_exc, low_ask_exc = exc2, exc1
        if exc2.bid > exc1.ask:
            relation = "gap"
        elif exc2.bid >= exc1.bid:
            relation = "intersection"
        else:
            relation = "inclusion"
    return relation, high_ask_exc, low_ask_exc


def compare_spreads(tickers):
    for ticker_pair in combinations(tickers, 2):
        get_positional_relation(ticker_pair[0], ticker_pair[1])


def get_status(exc1, exc2):
    RATIO_THRES = 2
    RATIO_THRES_HEAVY = 5

    ratio = exc1.balance_btc / exc2.balance_btc
    if ratio < RATIO_THRES and ratio > (1 / RATIO_THRES):
        status = "balanced"
    elif ratio < RATIO_THRES_HEAVY and ratio > (1 / RATIO_THRES_HEAVY):
        status = "unbalanced"
    else:
        status = "unbalanced_heavy"
    return status


def get_approach(high_ask_exc, low_ask_exc):
    if high_ask_exc.balance_btc > low_ask_exc.balance_btc:
        approach = "level"
    else:
        approach = "tilt"
    return approach


def get_size(trans_size_table, expectation, status, approach):
    trans_size = trans_size_table[
                    (trans_size_table["expectation"] == expectation) & 
                    (trans_size_table["credit_status"] == status) & 
                    (trans_size_table["approach"] == approach)
                 ]["credit_size"]
    return trans_size

def update_ticker_from_chart(exc, ticker):
    exc.ask = ticker.ask
    exc.bid = ticker.bid
    exc.timestamp = ticker.timestamp


if __name__ == "__main__":
    bf = BitFlyer()
    gc = GmoCoin()

    trans_size_table = pd.read_csv("data/transaction_size.csv")
    chart_bf = pd.read_csv("data/chart_bitflyer.csv")
    chart_gc = pd.read_csv("data/chart_gmocoin.csv")

    status = get_status(bf, gc)
    for ticker_bf, ticker_gc in zip(chart_bf.itertuples(), chart_gc.itertuples()):
        # update ticker
        update_ticker_from_chart(bf, ticker_bf)
        update_ticker_from_chart(gc, ticker_gc)

        relation, high_ask_exc, low_ask_exc = get_relation(bf, gc)
        if relation == "gap":
            expectation = get_margin_expectation(high_ask_exc, low_ask_exc)
            approach = get_approach(high_ask_exc, low_ask_exc)
            trans_size = get_size(trans_size_table, expectation, status, approach)
            print(expectation, approach, status)
            print(trans_size.at(-1)) ##???
            # transaction
            # sell_request()
            # buy_request()

            # update status

