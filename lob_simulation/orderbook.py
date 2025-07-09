"""
Order Book Implementation

This module implements a limit order book with price-time priority,
supporting limit orders, market orders, cancellations, and order book
reconstruction from market data feeds.
"""

import heapq
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
import pandas as pd

from .events import OrderEvent, CancelEvent, TradeEvent


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


class OrderBook:
    """
    Limit Order Book implementation with price-time priority.
    
    This class maintains separate bid and ask sides of the order book,
    with orders sorted by price (best first) and then by timestamp
    (earliest first) within each price level.
    """
    
    def __init__(self, tick_size: float = 0.01, max_levels: int = 10):
        """
        Initialize the order book.
        
        Args:
            tick_size: Minimum price increment
            max_levels: Maximum number of price levels to track
        """
        self.tick_size = tick_size
        self.max_levels = max_levels
        
        # Order storage
        self.orders: Dict[str, Order] = {}
        
        # Bid side (buy orders) - sorted by price descending
        self.bids: Dict[float, List[Order]] = defaultdict(list)
        self.bid_prices = []  # Sorted list of bid prices
        
        # Ask side (sell orders) - sorted by price ascending
        self.asks: Dict[float, List[Order]] = defaultdict(list)
        self.ask_prices = []  # Sorted list of ask prices
        
        # Market statistics
        self.best_bid = 0.0
        self.best_ask = float('inf')
        self.mid_price = 0.0
        self.spread = float('inf')
        
        # Volume tracking
        self.bid_volume = defaultdict(int)
        self.ask_volume = defaultdict(int)
        
        # Trade history
        self.trades = []
        
    def add_order(self, order_event: OrderEvent, current_time: float = None) -> List[TradeEvent]:
        """
        Add an order to the order book.
        
        Args:
            order_event: Order event to process
            current_time: The current simulation time (for trade timestamps)
            
        Returns:
            List of trade events that occurred
        """
        order = Order(
            order_id=order_event.order_id,
            trader_id=order_event.trader_id,
            side=order_event.side,
            price=order_event.price,
            quantity=order_event.quantity,
            timestamp=order_event.timestamp,
            order_type=order_event.order_type
        )
        
        trades = []
        
        if order.side == 'buy':
            trades = self._process_buy_order(order, current_time)
        else:
            trades = self._process_sell_order(order, current_time)
        
        # Update market statistics
        self._update_market_stats()
        
        return trades
    
    def _process_buy_order(self, order: Order, current_time: float = None) -> List[TradeEvent]:
        """Process a buy order."""
        trades = []
        remaining_quantity = order.quantity
        
        # Try to match against existing ask orders
        while remaining_quantity > 0 and self.ask_prices and order.price >= self.ask_prices[0]:
            best_ask_price = self.ask_prices[0]
            ask_orders = self.asks[best_ask_price]
            
            if not ask_orders:
                # Remove empty price level
                self.ask_prices.pop(0)
                continue
            
            # Safety check for empty orders list
            if not ask_orders:
                continue
            
            # Match with the oldest ask order
            ask_order = ask_orders[0]
            trade_quantity = min(remaining_quantity, ask_order.visible_quantity or 0)
            
            # Create trade
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
            
            # Update quantities
            remaining_quantity -= trade_quantity
            if ask_order.visible_quantity is not None:
                ask_order.visible_quantity -= trade_quantity
            
            # Remove ask order if fully filled
            if ask_order.visible_quantity == 0:
                ask_orders.pop(0)
                self.ask_volume[best_ask_price] -= ask_order.quantity
                
                # Remove from orders dict (safely)
                if ask_order.order_id in self.orders:
                    del self.orders[ask_order.order_id]
        
        # Add remaining quantity as limit order
        if remaining_quantity > 0:
            order.quantity = remaining_quantity
            order.visible_quantity = remaining_quantity
            self._add_limit_order(order)
        
        return trades
    
    def _process_sell_order(self, order: Order, current_time: float = None) -> List[TradeEvent]:
        """Process a sell order."""
        trades = []
        remaining_quantity = order.quantity
        
        # Try to match against existing bid orders
        while remaining_quantity > 0 and self.bid_prices and order.price <= self.bid_prices[0]:
            best_bid_price = self.bid_prices[0]
            bid_orders = self.bids[best_bid_price]
            
            if not bid_orders:
                # Remove empty price level
                self.bid_prices.pop(0)
                continue
            
            # Safety check for empty orders list
            if not bid_orders:
                continue
            
            # Match with the oldest bid order
            bid_order = bid_orders[0]
            trade_quantity = min(remaining_quantity, bid_order.visible_quantity or 0)
            
            # Create trade
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
            
            # Update quantities
            remaining_quantity -= trade_quantity
            if bid_order.visible_quantity is not None:
                bid_order.visible_quantity -= trade_quantity
            
            # Remove bid order if fully filled
            if bid_order.visible_quantity == 0:
                bid_orders.pop(0)
                self.bid_volume[best_bid_price] -= bid_order.quantity
                
                # Remove from orders dict (safely)
                if bid_order.order_id in self.orders:
                    del self.orders[bid_order.order_id]
        
        # Add remaining quantity as limit order
        if remaining_quantity > 0:
            order.quantity = remaining_quantity
            order.visible_quantity = remaining_quantity
            self._add_limit_order(order)
        
        return trades
    
    def _add_limit_order(self, order: Order):
        """Add a limit order to the appropriate side."""
        self.orders[order.order_id] = order
        
        if order.side == 'buy':
            self._add_bid_order(order)
        else:
            self._add_ask_order(order)
    
    def _add_bid_order(self, order: Order):
        """Add a bid order to the bid side."""
        price = order.price
        
        # Add to bid orders
        self.bids[price].append(order)
        self.bid_volume[price] += order.quantity
        
        # Maintain sorted bid prices
        if price not in self.bid_prices:
            self.bid_prices.append(price)
            self.bid_prices.sort(reverse=True)  # Best bid first
    
    def _add_ask_order(self, order: Order):
        """Add an ask order to the ask side."""
        price = order.price
        
        # Add to ask orders
        self.asks[price].append(order)
        self.ask_volume[price] += order.quantity
        
        # Maintain sorted ask prices
        if price not in self.ask_prices:
            self.ask_prices.append(price)
            self.ask_prices.sort()  # Best ask first
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            True if order was cancelled, False if not found
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Remove from appropriate side
        if order.side == 'buy':
            self._remove_bid_order(order)
        else:
            self._remove_ask_order(order)
        
        # Remove from orders dict
        del self.orders[order_id]
        
        # Update market statistics
        self._update_market_stats()
        
        return True
    
    def _remove_bid_order(self, order: Order):
        """Remove a bid order."""
        price = order.price
        orders_at_price = self.bids[price]
        
        # Find and remove the order
        for i, existing_order in enumerate(orders_at_price):
            if existing_order.order_id == order.order_id:
                orders_at_price.pop(i)
                self.bid_volume[price] -= order.quantity
                break
        
        # Remove price level if empty
        if not orders_at_price:
            del self.bids[price]
            self.bid_prices.remove(price)
    
    def _remove_ask_order(self, order: Order):
        """Remove an ask order."""
        price = order.price
        orders_at_price = self.asks[price]
        
        # Find and remove the order
        for i, existing_order in enumerate(orders_at_price):
            if existing_order.order_id == order.order_id:
                orders_at_price.pop(i)
                self.ask_volume[price] -= order.quantity
                break
        
        # Remove price level if empty
        if not orders_at_price:
            del self.asks[price]
            self.ask_prices.remove(price)
    
    def _update_market_stats(self):
        """Update market statistics."""
        # Update best bid/ask
        self.best_bid = self.bid_prices[0] if self.bid_prices else 0.0
        self.best_ask = self.ask_prices[0] if self.ask_prices else float('inf')
        
        # Update mid price and spread
        if self.best_bid > 0 and self.best_ask < float('inf'):
            self.mid_price = (self.best_bid + self.best_ask) / 2
            self.spread = self.best_ask - self.best_bid
        else:
            self.mid_price = 0.0
            self.spread = float('inf')
    
    def get_bid_volume(self) -> int:
        """Get total volume at best bid."""
        if not self.bid_prices:
            return 0
        return self.bid_volume[self.bid_prices[0]]
    
    def get_ask_volume(self) -> int:
        """Get total volume at best ask."""
        if not self.ask_prices:
            return 0
        return self.ask_volume[self.ask_prices[0]]
    
    def get_depth(self, levels: int = 5) -> Dict[str, List[Tuple[float, int]]]:
        """
        Get order book depth.
        
        Args:
            levels: Number of price levels to return
            
        Returns:
            Dictionary with 'bids' and 'asks' lists of (price, volume) tuples
        """
        bids = []
        for price in self.bid_prices[:levels]:
            bids.append((price, self.bid_volume[price]))
        
        asks = []
        for price in self.ask_prices[:levels]:
            asks.append((price, self.ask_volume[price]))
        
        return {'bids': bids, 'asks': asks}
    
    def get_state(self) -> Dict[str, Any]:
        """Get current order book state."""
        return {
            'best_bid': self.best_bid,
            'best_ask': self.best_ask,
            'mid_price': self.mid_price,
            'spread': self.spread,
            'bid_volume': self.get_bid_volume(),
            'ask_volume': self.get_ask_volume(),
            'depth': self.get_depth(),
            'num_orders': len(self.orders),
            'num_trades': len(self.trades)
        }
    
    def reset(self):
        """Reset the order book to initial state."""
        self.orders.clear()
        self.bids.clear()
        self.asks.clear()
        self.bid_prices.clear()
        self.ask_prices.clear()
        self.bid_volume.clear()
        self.ask_volume.clear()
        self.trades.clear()
        self.best_bid = 0.0
        self.best_ask = float('inf')
        self.mid_price = 0.0
        self.spread = float('inf') 