from dataclasses import dataclass
from typing import Any
from .base import Event, EventType

@dataclass
class CancelEvent(Event):
    """Represents an order cancellation."""
    order_id: str
    trader_id: str

    def __init__(self, order_id: str, trader_id: str, timestamp: float):
        super().__init__(EventType.CANCEL, timestamp)
        self.order_id = order_id
        self.trader_id = trader_id

    def process(self) -> Any:
        """Process the cancel event."""
        return {
            'order_id': self.order_id,
            'trader_id': self.trader_id,
            'timestamp': self.timestamp
        }
