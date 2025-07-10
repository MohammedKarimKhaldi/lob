# Events Module Documentation

This module defines all event types and the event queue for the simulation.

---

## EventType

```python
class EventType(Enum):
    """Types of events in the simulation."""
    ORDER = "order"
    CANCEL = "cancel"
    TRADE = "trade"
    MARKET_DATA = "market_data"
```

---

## Event (Base Class)

```python
class Event(ABC):
    """Base class for all events in the simulation."""
    def __init__(self, event_type: EventType, timestamp: float)
    def process(self) -> Any
```
- All event types inherit from this class.
- `process()` must be implemented by subclasses.

---

## OrderEvent

```python
@dataclass
class OrderEvent(Event):
    """Represents a new order being placed."""
    order_id: str
    trader_id: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: int
    order_type: str = 'limit'  # 'limit', 'market', 'iceberg', 'reserve'
    def process(self) -> Any
```
- Used to represent new orders in the simulation.
- `process()` returns a dict with all order details.

---

## CancelEvent

```python
@dataclass
class CancelEvent(Event):
    """Represents an order cancellation."""
    order_id: str
    trader_id: str
    def process(self) -> Any
```
- Used to represent order cancellations.
- `process()` returns a dict with cancellation details.

---

## TradeEvent

```python
@dataclass
class TradeEvent(Event):
    """Represents a trade execution."""
    trade_id: str
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int
    def process(self) -> Any
```
- Used to represent trade executions.
- `process()` returns a dict with trade details.

---

## MarketDataEvent

```python
@dataclass
class MarketDataEvent(Event):
    """Represents market data updates."""
    best_bid: float
    best_ask: float
    mid_price: float
    spread: float
    bid_volume: int
    ask_volume: int
    def process(self) -> Any
```
- Used to represent market data updates.
- `process()` returns a dict with market data details.

---

## EventQueue

```python
class EventQueue:
    """Priority queue for managing events in chronological order."""
    def add_event(self, event: Event)
    def get_next_event(self) -> Optional[Event]
    def peek_next_event(self) -> Optional[Event]
    def is_empty(self) -> bool
    def size(self) -> int
```
- Used to manage and process events in time order.

---

## Example Usage

```python
from lob_simulation.events import OrderEvent, CancelEvent, TradeEvent, MarketDataEvent, EventQueue

queue = EventQueue()
order_event = OrderEvent('oid1', 'trader1', 'buy', 100.0, 10, timestamp=0.0)
queue.add_event(order_event)
next_event = queue.get_next_event()
if next_event:
    result = next_event.process()
```

---

## Extending
- To add a new event type, subclass `Event`, implement `process()`, and register in `lob_simulation/events/__init__.py`.

---

## Reference
- Events are used throughout the simulation engine to represent all actions and state changes. 