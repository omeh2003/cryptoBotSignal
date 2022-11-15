import datetime
import os
import sys
import time

from loguru import logger

from app.Config import Config
from app.Broker import Broker
from app.Data import PriceDataLoader


class Bot:

    def __init__(self, config: 'Config'):
        self._config = config
        self._price_loader = PriceDataLoader()
        self._broker = Broker(config.total_cash, self._price_loader)
        self._data: None
        self._is_running = False
        self.setup_logging()

    def setup_logging(self):
        today = datetime.datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        log_file_name = f"{today_str}_bot_log.txt"
        log_full_path = os.path.join(os.path.abspath(os.path.curdir), log_file_name)
        open(log_full_path, 'w').close()
        logger.remove()
        logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>{level}</red> {message}",
                   colorize=True)
        logger.add(log_full_path, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")

    def start(self):
        logger.info("Starting bot")
        self._is_running = True
        while self._is_running:
            symbols = self._config.symbols
            for symbol in symbols:
                data_df = self._price_loader.load(symbol, 'usd')
                strategy = Strategy(symbol, self._broker, self._config.cash_per_trade)
                strategy.execute(data_df)
            self._broker.check_order_status()
            logger.info(self._broker.describe())
            time.sleep(self._config.data_fetch_interval)

    def stop(self):
        logger.info("Stopping bot")
        self._is_running = True
