import datetime

import pandas as pd
import requests
from loguru import logger
from pandas import DataFrame


class PriceDataLoader:

    def __init__(self):
        self._last_refresh_date = None
        self._data_map = {}

    def fetch_coin_price_data(self, symbol, currency):
        try:
            fetch_url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency={currency}&days=7"
            headers = {
                'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
                'Accept':          'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            #  Send GET request
            response = requests.get(fetch_url, headers=headers)
            data = response.json()
            df = pd.DataFrame({'Unix': [], 'Open': [], 'High': [], 'Low': [], 'Close': []})
            for item in data:
                row = pd.DataFrame(
                    {'Unix': [item[0]], 'Open': [item[1]], 'High': [item[2]], 'Low': [item[3]], 'Close': [item[4]]})
                row['Date'] = pd.to_datetime(row['Unix'])
                df = pd.concat([df, row], axis=0, ignore_index=True)
            df.set_index(df['Date'])
            self._data_map[symbol] = df
            return df
        except Exception as e:
            print('Error loading trending coins, ', e)
            return None

    def load(self, symbol, currency):
        logger.info(f"DataLoader: Starting data load at {datetime.datetime.now().__str__()} for symbol {symbol}")
        self._data = self.fetch_coin_price_data(symbol, currency)
        self._last_refresh_date = datetime.datetime.now().__str__()
        return self._data

    #  Getters
    @property
    def data(self) -> DataFrame:
        return self._data

    @property
    def last_refresh_date(self) -> str:
        return self._last_refresh_date

    def last_price(self, symbol: str) -> float:
        if symbol in self._data_map:
            df = self._data_map[symbol]
            return df['Close'].iloc[-1]
        else:
            return 0
