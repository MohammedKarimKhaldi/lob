from dataclasses import dataclass
from typing import Optional

@dataclass
class Order:
    """Represents a limit order in the order book."""
    order_id: str
    trader_id: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: int
    timestamp: float
    order_type: str = 'limit'  # 'limit', 'market', 'iceberg', 'reserve'
    visible_quantity: Optional[int] = None
    hidden_quantity: Optional[int] = None

    def __post_init__(self):
        if self.visible_quantity is None:
            self.visible_quantity = self.quantity
        if self.hidden_quantity is None:
            self.hidden_quantity = 0
