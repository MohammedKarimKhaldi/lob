from dataclasses import dataclass
from typing import Any
from .base import Event, EventType

@dataclass
class TradeEvent(Event):
    """Represents a trade execution."""
    trade_id: str
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int

    def __init__(self, trade_id: str, buy_order_id: str, sell_order_id: str,
                 price: float, quantity: int, timestamp: float):
        super().__init__(EventType.TRADE, timestamp)
        self.trade_id = trade_id
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.quantity = quantity

    def process(self) -> Any:
        """Process the trade event."""
        return {
            'trade_id': self.trade_id,
            'buy_order_id': self.buy_order_id,
            'sell_order_id': self.sell_order_id,
            'price': self.price,
            'quantity': self.quantity,
            'timestamp': self.timestamp
        }
