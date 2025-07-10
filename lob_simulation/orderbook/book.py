from collections import defaultdict
from typing import Dict, List, Any, Tuple
from .order import Order
from .matching import (
    process_buy_order, process_sell_order, add_limit_order, add_bid_order, add_ask_order,
    cancel_order as matching_cancel_order, remove_bid_order, remove_ask_order
)
from .state import (
    update_market_stats, get_bid_volume, get_ask_volume, get_depth, get_state as state_get_state, reset as state_reset
)
from lob_simulation.events import OrderEvent, TradeEvent

class OrderBook:
    def __init__(self, tick_size: float = 0.01, max_levels: int = 10):
        self.tick_size = tick_size
        self.max_levels = max_levels
        self.orders: Dict[str, Order] = {}
        self.bids: Dict[float, List[Order]] = defaultdict(list)
        self.bid_prices = []
        self.asks: Dict[float, List[Order]] = defaultdict(list)
        self.ask_prices = []
        self.best_bid = 0.0
        self.best_ask = float('inf')
        self.mid_price = 0.0
        self.spread = float('inf')
        self.bid_volume = defaultdict(int)
        self.ask_volume = defaultdict(int)
        self.trades = []

    def add_order(self, order_event: OrderEvent, current_time: float = 0.0) -> List[TradeEvent]:
        order = Order(
            order_id=order_event.order_id,
            trader_id=order_event.trader_id,
            side=order_event.side,
            price=order_event.price,
            quantity=order_event.quantity,
            timestamp=order_event.timestamp,
            order_type=order_event.order_type
        )
        if order.side == 'buy':
            trades = process_buy_order(self, order, current_time)
        else:
            trades = process_sell_order(self, order, current_time)
        update_market_stats(self)
        return trades

    def cancel_order(self, order_id: str) -> bool:
        result = matching_cancel_order(self, order_id)
        update_market_stats(self)
        return result

    def get_bid_volume(self) -> int:
        return get_bid_volume(self)

    def get_ask_volume(self) -> int:
        return get_ask_volume(self)

    def get_depth(self, levels: int = 5) -> Dict[str, List[Tuple[float, int]]]:
        return get_depth(self, levels)

    def get_state(self) -> Dict[str, Any]:
        return state_get_state(self)

    def reset(self):
        state_reset(self)
