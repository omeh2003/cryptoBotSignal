import os
import sys
import ccxt
import pandas as pd
from ccxt import binanceusdm


class GetData:
    exchange: ccxt

    def __init__(self):
        self.values = None
        self.widths = None
        self.keys = None
        self.first = None
        self.ohlcvs = None
        self.exchange = ccxt.binanceusdm()
        self.timeframe = '15m'
        self.limit = 1
        self.symbol = 'BTC/USDT'
        self.exchange.load_markets()
        self.ohlcv = self.exchange.fetch_ohlcv(self.symbol)
        self.ohlcv = self.ohlcv.sort(key=lambda d: d[0])
        self.market = self.exchange.market(self.symbol)
        self.params = {
            'pair':         self.market['id'],
            'contractType': 'PERPETUAL',
            # 'PERPETUAL', 'CURRENT_MONTH', 'NEXT_MONTH', 'CURRENT_QUARTER', 'NEXT_QUARTER'
            'interval':     self.exchange.timeframes[self.timeframe],
        }
        self.DataFrameMarket = None

    def updatedate(self):
        self.values = [[self.exchange.iso8601(int(o[0]))] + o[1:] for o in self.ohlcvs]
        self.first = self.values[0]
        self.keys = list(self.first.keys()) if isinstance(self.first, dict) else range(0, len(self.first))
        self.widths = [max([len(str(v[k])) for v in self.values]) for k in self.keys]
        self.DataFrameMarket = pd.DataFrame(self.values,
                                            columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                                     'Quote asset volume',
                                                     'Number of trades', 'Taker buy base asset volume',
                                                     'Taker buy quote asset volume',
                                                     'Ignore'])
        self.DataFrameMarket.drop(columns=['Close time',
                                           'Quote asset volume',
                                           'Number of trades',
                                           'Taker buy base asset volume',
                                           'Taker buy quote asset volume',
                                           'Ignore'], axis=0, inplace=True)
        self.DataFrameMarket['Date'] = pd.to_datetime(self.DataFrameMarket['Date'])
        self.DataFrameMarket['Open'] = pd.to_numeric(self.DataFrameMarket['Open'])
        self.DataFrameMarket['High'] = pd.to_numeric(self.DataFrameMarket['High'])
        self.DataFrameMarket['Low'] = pd.to_numeric(self.DataFrameMarket['Low'])
        self.DataFrameMarket['Close'] = pd.to_numeric(self.DataFrameMarket['Close'])
        self.DataFrameMarket['Volume'] = pd.to_numeric(self.DataFrameMarket['Volume'])

        self.DataFrameMarket.set_index('Date', inplace=True)

    def updatemarket(self):
        try:
            self.exchange.load_markets()
            self.ohlcvs = self.exchange.fapiPublic_get_continuousklines(self.params)
        except Exception as e:
            print(type(e).__name__, str(e))

    def renew(self):
        self.updatemarket()
        self.updatedate()
