from dataclasses import dataclass
from typing import Any
from .base import Event, EventType

@dataclass
class OrderEvent(Event):
    """Represents a new order being placed."""
    order_id: str
    trader_id: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: int
    order_type: str = 'limit'  # 'limit', 'market', 'iceberg', 'reserve'

    def __init__(self, order_id: str, trader_id: str, side: str, price: float, 
                 quantity: int, timestamp: float, order_type: str = 'limit'):
        super().__init__(EventType.ORDER, timestamp)
        self.order_id = order_id
        self.trader_id = trader_id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.order_type = order_type

    def process(self) -> Any:
        """Process the order event."""
        return {
            'order_id': self.order_id,
            'trader_id': self.trader_id,
            'side': self.side,
            'price': self.price,
            'quantity': self.quantity,
            'order_type': self.order_type,
            'timestamp': self.timestamp
        }
