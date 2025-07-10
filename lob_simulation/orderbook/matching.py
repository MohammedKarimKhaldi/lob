from .order import Order
from typing import List
from lob_simulation.events import TradeEvent

# Each function below takes the OrderBook instance as the first argument (self)

def process_buy_order(self, order: Order, current_time: float = 0.0) -> List[TradeEvent]:
    trades = []
    remaining_quantity = order.quantity
    while remaining_quantity > 0 and self.ask_prices and order.price >= self.ask_prices[0]:
        best_ask_price = self.ask_prices[0]
        ask_orders = self.asks[best_ask_price]
        if not ask_orders:
            self.ask_prices.pop(0)
            continue
        ask_order = ask_orders[0]
        trade_quantity = min(remaining_quantity, ask_order.visible_quantity or 0)
        trade = TradeEvent(
            trade_id=f"trade_{len(self.trades)}",
            buy_order_id=order.order_id,
            sell_order_id=ask_order.order_id,
            price=best_ask_price,
            quantity=trade_quantity,
            timestamp=current_time if current_time is not None else order.timestamp
        )
        trades.append(trade)
        self.trades.append(trade)
        remaining_quantity -= trade_quantity
        if ask_order.visible_quantity is not None:
            ask_order.visible_quantity -= trade_quantity
        if ask_order.visible_quantity == 0:
            ask_orders.pop(0)
            self.ask_volume[best_ask_price] -= ask_order.quantity
            if ask_order.order_id in self.orders:
                del self.orders[ask_order.order_id]
    if remaining_quantity > 0:
        order.quantity = remaining_quantity
        order.visible_quantity = remaining_quantity
        add_limit_order(self, order)
    return trades

def process_sell_order(self, order: Order, current_time: float = 0.0) -> List[TradeEvent]:
    trades = []
    remaining_quantity = order.quantity
    while remaining_quantity > 0 and self.bid_prices and order.price <= self.bid_prices[0]:
        best_bid_price = self.bid_prices[0]
        bid_orders = self.bids[best_bid_price]
        if not bid_orders:
            self.bid_prices.pop(0)
            continue
        bid_order = bid_orders[0]
        trade_quantity = min(remaining_quantity, bid_order.visible_quantity or 0)
        trade = TradeEvent(
            trade_id=f"trade_{len(self.trades)}",
            buy_order_id=bid_order.order_id,
            sell_order_id=order.order_id,
            price=best_bid_price,
            quantity=trade_quantity,
            timestamp=current_time if current_time is not None else order.timestamp
        )
        trades.append(trade)
        self.trades.append(trade)
        remaining_quantity -= trade_quantity
        if bid_order.visible_quantity is not None:
            bid_order.visible_quantity -= trade_quantity
        if bid_order.visible_quantity == 0:
            bid_orders.pop(0)
            self.bid_volume[best_bid_price] -= bid_order.quantity
            if bid_order.order_id in self.orders:
                del self.orders[bid_order.order_id]
    if remaining_quantity > 0:
        order.quantity = remaining_quantity
        order.visible_quantity = remaining_quantity
        add_limit_order(self, order)
    return trades

def add_limit_order(self, order: Order):
    self.orders[order.order_id] = order
    if order.side == 'buy':
        add_bid_order(self, order)
    else:
        add_ask_order(self, order)

def add_bid_order(self, order: Order):
    price = order.price
    self.bids[price].append(order)
    self.bid_volume[price] += order.quantity
    if price not in self.bid_prices:
        self.bid_prices.append(price)
        self.bid_prices.sort(reverse=True)

def add_ask_order(self, order: Order):
    price = order.price
    self.asks[price].append(order)
    self.ask_volume[price] += order.quantity
    if price not in self.ask_prices:
        self.ask_prices.append(price)
        self.ask_prices.sort()

def cancel_order(self, order_id: str) -> bool:
    if order_id not in self.orders:
        return False
    order = self.orders[order_id]
    if order.side == 'buy':
        remove_bid_order(self, order)
    else:
        remove_ask_order(self, order)
    del self.orders[order_id]
    return True

def remove_bid_order(self, order: Order):
    price = order.price
    orders_at_price = self.bids[price]
    for i, existing_order in enumerate(orders_at_price):
        if existing_order.order_id == order.order_id:
            orders_at_price.pop(i)
            self.bid_volume[price] -= order.quantity
            break
    if not orders_at_price:
        del self.bids[price]
        self.bid_prices.remove(price)

def remove_ask_order(self, order: Order):
    price = order.price
    orders_at_price = self.asks[price]
    for i, existing_order in enumerate(orders_at_price):
        if existing_order.order_id == order.order_id:
            orders_at_price.pop(i)
            self.ask_volume[price] -= order.quantity
            break
    if not orders_at_price:
        del self.asks[price]
        self.ask_prices.remove(price)
