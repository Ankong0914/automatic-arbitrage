"""
Reference:
https://github.com/bokeh/bokeh/blob/master/examples/plotting/server/animated.py
"""

import numpy as np
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource, Div, Patch
from bokeh.layouts import gridplot, column
from bokeh.client import push_session
import time


from exchanges.liquid import Liquid
from exchanges.gmo_coin import GmoCoin
from exchanges.coin_check import CoinCheck
from exchanges.bit_flyer import BitFlyer
from exchanges.utils import send_async_requests


class Chart:
    def __init__(self, exchanges):
        self.exchanges = exchanges
        self.color = ["#a6cee3", "#b2df8a"]
        self.source = {
            exc.NAME: None for exc in exchanges
        }
        self.glyph = {
            exc.NAME: None for exc in exchanges
        }
        self.ask_data = {
            exc.NAME: [] for exc in exchanges 
        }
        self.bid_data = {
            exc.NAME: [] for exc in exchanges 
        }


    def update(self):
        # funcs = (self.exchanges[0].ticker.fetch, self.exchanges[1].ticker.fetch)
        # send_async_requests(funcs)
        self.exchanges[0].ticker.fetch()
        self.exchanges[1].ticker.fetch()

        for exchange in self.exchanges:
            self.bid_data[exchange.NAME].append(exchange.ticker.bid) 
            bid = np.array(self.bid_data[exchange.NAME])
            bid_x = np.arange(len(bid))
            
            self.ask_data[exchange.NAME].append(exchange.ticker.ask) 
            ask = np.flipud(np.array(self.ask_data[exchange.NAME]))
            ask_x = np.flipud(np.arange(len(ask)))

            x = np.hstack((bid_x, ask_x))
            y = np.hstack((bid, ask))

            self.source[exchange.NAME].data = dict(x=x, y=y)


    def main(self):
        p = figure(
            title="ticker change",  # グラフのタイトル
            plot_width=1200,      # グラフの横幅
            plot_height=600,     # グラフの縦幅 
            x_axis_label='time',    # x軸のラベル
            y_axis_label='price',    # x軸のラベル
            # x_axis_type="log"  # 軸タイプ
        )

        self.exchanges[0].ticker.fetch()
        self.exchanges[1].ticker.fetch()

        for i, exchange in enumerate(self.exchanges):
            self.bid_data[exchange.NAME].append(exchange.ticker.bid) 
            bid = np.array(self.bid_data[exchange.NAME])
            bid_x = np.arange(len(bid))
            
            self.ask_data[exchange.NAME].append(exchange.ticker.ask) 
            ask = np.flipud(np.array(self.ask_data[exchange.NAME]))
            ask_x = np.flipud(np.arange(len(ask)))

            x = np.hstack((bid_x, ask_x))
            y = np.hstack((bid, ask))
            self.source[exchange.NAME] = ColumnDataSource(dict(x=x, y=y))
            self.glyph[exchange.NAME] = Patch(x="x", y="y", fill_color=self.color[i], fill_alpha=0.5)
            p.add_glyph(self.source[exchange.NAME], self.glyph[exchange.NAME])

        document = curdoc()
        document.add_root(p)
        document.add_periodic_callback(self.update, 1000)

exchanges = [Liquid(), GmoCoin()]
chart = Chart(exchanges)
chart.main()