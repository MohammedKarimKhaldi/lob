"""
Event System for Limit Order Book Simulation

This module defines all event types used in the simulation, including
order events, cancellation events, and trade events.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum


class EventType(Enum):
    """Types of events in the simulation."""
    ORDER = "order"
    CANCEL = "cancel"
    TRADE = "trade"
    MARKET_DATA = "market_data"


class Event(ABC):
    """Base class for all events in the simulation."""
    
    def __init__(self, event_type: EventType, timestamp: float):
        self.event_type = event_type
        self.timestamp = timestamp
    
    @abstractmethod
    def process(self) -> Any:
        """Process the event and return any results."""
        pass


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


class EventQueue:
    """Priority queue for managing events in chronological order."""
    
    def __init__(self):
        self.events = []
    
    def add_event(self, event: Event):
        """Add an event to the queue."""
        import time
        import heapq
        heapq.heappush(self.events, (event.timestamp, time.time(), event))
    
    def get_next_event(self) -> Optional[Event]:
        """Get the next event from the queue."""
        import heapq
        if self.events:
            _, _, event = heapq.heappop(self.events)
            return event
        return None
    
    def peek_next_event(self) -> Optional[Event]:
        """Peek at the next event without removing it."""
        if self.events:
            _, _, event = self.events[0]
            return event
        return None
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self.events) == 0
    
    def size(self) -> int:
        """Get the number of events in the queue."""
        return len(self.events) 