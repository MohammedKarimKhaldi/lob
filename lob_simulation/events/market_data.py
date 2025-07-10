from dataclasses import dataclass
from typing import Any
from .base import Event, EventType

@dataclass
class MarketDataEvent(Event):
    """Represents market data updates."""
    best_bid: float
    best_ask: float
    mid_price: float
    spread: float
    bid_volume: int
    ask_volume: int

    def __init__(self, best_bid: float, best_ask: float, mid_price: float,
                 spread: float, bid_volume: int, ask_volume: int, timestamp: float):
        super().__init__(EventType.MARKET_DATA, timestamp)
        self.best_bid = best_bid
        self.best_ask = best_ask
        self.mid_price = mid_price
        self.spread = spread
        self.bid_volume = bid_volume
        self.ask_volume = ask_volume

    def process(self) -> Any:
        """Process the market data event."""
        return {
            'best_bid': self.best_bid,
            'best_ask': self.best_ask,
            'mid_price': self.mid_price,
            'spread': self.spread,
            'bid_volume': self.bid_volume,
            'ask_volume': self.ask_volume,
            'timestamp': self.timestamp
        }
