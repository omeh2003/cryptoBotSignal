from typing import List

from loguru import logger

from app.Order import Order
from app.botsingle import Positions, Side, OrderStatus
from app.Trade import Trade


class Broker:
    def __init__(self, cash, price_loader):
        assert 0 < cash, f"Cash should be > 0, is {cash}"
        self._cash = cash
        self._price_loader = price_loader
        self._orders: List[Order] = []
        self._trades: List[Trade] = []
        self._closed_trades: List[Trade] = []

    def describe(self):
        open_trades_profit_loss = 0
        for trade in self._trades:
            open_trades_profit_loss += trade.profit_loss
        closed_trades_profit_loss = 0
        for trade in self._trades:
            closed_trades_profit_loss += trade.profit_loss
        return f'<Broker: Cash: {self._cash:.0f} Orders: {len(self._orders)} Trades: {len(self._trades)} Closed Trades: {len(self._closed_trades)} \
Open Trades P&L: {open_trades_profit_loss:.0f} Closed Trades P&L: {closed_trades_profit_loss:.0f}>'

    def submit_order(self,
                     symbol: str,
                     position: Positions,
                     side: Side,
                     size: float = None,
                     limit: float = None,
                     stop: float = None):
        size = size and float(size)
        stop = stop and float(stop)
        limit = limit and float(limit)
        if position == Positions.LONG and side == Side.SELL:
            for trade in reversed(self._trades):
                if trade.symbol == symbol and trade.position == position:
                    size = trade.size
        elif position == Positions.SHORT and side == Side.BUY:
            for trade in reversed(self._trades):
                if trade.symbol == symbol and trade.position == position:
                    size = trade.size
        if size is None:
            logger.error(
                f"Position {position}, side: {side} - Size not specified for sell request, matching trade not found")
            return
        order = Order(symbol, position, side, size, limit, stop)
        logger.info(f"Sending order: {order.describe()}")
        #  todo: Send order to exchange
        self._orders.insert(0, order)
        return order

    def check_order_status(self):
        logger.info('Checking order status')
        for order in list(self._orders):
            #  todo: Check order status with exchange
            order.set_status(OrderStatus.FILLED)
            current_price = self._price_loader.last_price(order.symbol)
            order.set_price(current_price)
            if order.status == OrderStatus.FILLED:
                if (order.position == Positions.LONG and order.side == Side.BUY) or \
                        (order.position == Positions.SHORT and order.side == Side.SELL):
                    trade = Trade(order.symbol, order.position, order.side, order.size, order.price, self._price_loader)
                    self._trades.insert(0, trade)
                    logger.info(f"Opened new trade {trade.describe()}")
                    if order.position == Positions.LONG:
                        self._cash -= order.size * order.price
                    else:
                        self._cash += order.size * order.price
                    self._orders.remove(order)
                    logger.info(f"Removed order {order.describe()}")
                elif (order.position == Positions.LONG and order.side == Side.SELL) or \
                        (order.position == Positions.SHORT and order.side == Side.BUY):
                    for trade in reversed(self._trades):
                        if trade.position == order.position and trade.side != order.side and trade.size == order.size:
                            trade.set_exit_price(order.price)
                            self._trades.remove(trade)
                            self._closed_trades.append(trade)
                            logger.info(f"Closed trade {trade.describe()}")
                            if order.position == Positions.LONG:
                                self._cash += order.size * order.price
                            else:
                                self._cash -= order.size * order.price
                            self._orders.remove(order)
                            logger.info(f"Removed order {order.describe()}")
