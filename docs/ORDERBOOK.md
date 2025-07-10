# Orderbook Module Documentation

This module implements the modular order book and matching engine for the simulation.

---

## Order (Dataclass)

```python
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
    def __post_init__(self)
```
- Represents an order in the book, with support for hidden/iceberg orders.

---

## OrderBook

```python
class OrderBook:
    def add_order(self, order_event: OrderEvent, current_time: float = 0.0) -> List[TradeEvent]
    def cancel_order(self, order_id: str) -> bool
    def get_bid_volume(self) -> int
    def get_ask_volume(self) -> int
    def get_depth(self, levels: int = 5) -> Dict[str, List[Tuple[float, int]]]
    def get_state(self) -> Dict[str, Any]
    def reset(self)
```
- Manages all orders, bids, asks, and trades.
- Provides methods to add/cancel orders, query depth, and reset state.

---

## Matching Logic

- `process_buy_order(self, order: Order, current_time: float = 0.0) -> List[TradeEvent]`
- `process_sell_order(self, order: Order, current_time: float = 0.0) -> List[TradeEvent]`
- `add_limit_order(self, order: Order)`
- `add_bid_order(self, order: Order)`
- `add_ask_order(self, order: Order)`
- `cancel_order(self, order_id: str) -> bool`
- `remove_bid_order(self, order: Order)`
- `remove_ask_order(self, order: Order)`

These functions implement price-time priority matching, order book updates, and order cancellation.

---

## State Logic

- `update_market_stats(self)` — Updates best bid/ask, mid price, and spread.
- `get_bid_volume(self) -> int` — Returns volume at best bid.
- `get_ask_volume(self) -> int` — Returns volume at best ask.
- `get_depth(self, levels: int = 5)` — Returns price/volume tuples for top N levels.
- `get_state(self)` — Returns a dict with all current order book state.
- `reset(self)` — Clears all orders and resets state.

---

## Example Usage

```python
from lob_simulation.orderbook import OrderBook
from lob_simulation.events import OrderEvent

orderbook = OrderBook(tick_size=0.01, max_levels=10)
order_event = OrderEvent('oid1', 'trader1', 'buy', 100.0, 10, timestamp=0.0)
trades = orderbook.add_order(order_event)
state = orderbook.get_state()
```

---

## Extending
- To add new order types, extend the `Order` dataclass and update matching logic as needed.
- To add new matching rules, modify or add functions in `matching.py`.
- For new state or analytics, extend `state.py`.

---

## Reference
- The order book is used throughout the simulation engine to manage all orders, trades, and market state. 