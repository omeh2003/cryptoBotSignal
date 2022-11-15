import datetime
import os
from loguru import logger
import sys
from enum import Enum

from app.Bot import Bot
from app.Config import Config

LOG_DIR = os.path.abspath(os.curdir)


class Positions(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderStatus(Enum):
    PENDING = 'PENDING'
    CANCELED = 'CANCELED'
    FILLED = 'FILLED'


def setup_logging(self):
    today = datetime.datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    log_file_name = f"{today_str}_bot_log.txt"
    log_full_path = os.path.join(LOG_DIR, log_file_name)
    open(log_full_path, 'w').close()
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>{level}</red> {message}",
               colorize=True)
    logger.add(log_full_path, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")


if __name__ == '__main__':
    config = Config(symbols=['BTC', 'USDT'], cash_per_trade=100, total_cash=10000, data_fetch_interval=60)
    bot = Bot(config)
    bot.start()
