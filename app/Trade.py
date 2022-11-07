import datetime
import uuid
from typing import Optional

from app.botsingle import Positions, Side


class Trade:

    def __init__(self, symbol: str, position: Positions, side: Side, size: int, entry_price: float,
                 price_loader: 'PriceDataLoader'):
        self._id = str(uuid.uuid4())
        self._symbol = symbol
        self._position = position
        self._side = side
        self._size = size
        self._entry_price = entry_price
        self._exit_price: Optional[float] = None
        self._entry_date = datetime.datetime.now().__str__()
        self._exit_date: str = None
        self._price_loader = price_loader

    def describe(self):
        return f'<Trade id: {self._id} symbol: {self._symbol} size: {self._size} entry_date: {self._entry_date} exit date: {self._exit_date or ""}' \
               f'entry price: {self._entry_price} exit price: {self._exit_price or ""} pl: {self.profit_loss_pct}>'

    @property
    def id(self) -> str:
        return self._id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def position(self) -> Positions:
        return self._position

    @property
    def side(self) -> Side:
        return self._side

    @property
    def size(self) -> float:
        return self._size

    @property
    def entry_date(self) -> str:
        return self._entry_date

    @property
    def exit_date(self) -> Optional[str]:
        return self._exit_date

    @property
    def entry_price(self) -> float:
        return self._entry_price

    @property
    def exit_price(self) -> Optional[float]:
        return self._exit_price

    @property
    def profit_loss(self):
        price = self._exit_price or self._price_loader.last_price(self._symbol)
        return self._size * (price - self._entry_price)

    @property
    def profit_loss_pct(self):
        price = self._exit_price or self._price_loader.last_price(self._symbol)
        return self._size * (price / self._entry_price - 1)

    def set_exit_price(self, exit_price):
        self._exit_price = exit_price
