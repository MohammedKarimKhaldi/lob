"""
Market Making Strategy

A simple market making strategy that places orders on both sides
of the order book to capture the spread.
"""

import random
from typing import Dict, List, Any
from .base import BaseStrategy, StrategyConfig
from ..events import OrderEvent


class MarketMakingStrategy(BaseStrategy):
    """Market making strategy implementation."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.order_id_counter = 0
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate market making orders."""
        orders = []
        
        # Update market data
        self.update_market_data(market_data)
        
        # Check if we should place orders
        if not self.is_active or self.spread < self.config.min_spread:
            return orders
        
        # Calculate order sizes based on position
        max_buy_size = min(
            self.config.max_order_size,
            self.config.max_position - self.performance.current_position
        )
        max_sell_size = min(
            self.config.max_order_size,
            self.config.max_position + self.performance.current_position
        )
        
        # Place buy order
        if max_buy_size > 0:
            buy_price = self.best_bid + self.config.tick_size
            buy_order = OrderEvent(
                order_id=f"mm_buy_{self.order_id_counter}",
                trader_id=self.config.strategy_name,
                side="buy",
                order_type="limit",
                quantity=max_buy_size,
                price=buy_price,
                timestamp=current_time
            )
            orders.append(buy_order)
            self.active_orders[buy_order.order_id] = buy_order
            self.order_id_counter += 1
        
        # Place sell order
        if max_sell_size > 0:
            sell_price = self.best_ask - self.config.tick_size
            sell_order = OrderEvent(
                order_id=f"mm_sell_{self.order_id_counter}",
                trader_id=self.config.strategy_name,
                side="sell",
                order_type="limit",
                quantity=max_sell_size,
                price=sell_price,
                timestamp=current_time
            )
            orders.append(sell_order)
            self.active_orders[sell_order.order_id] = sell_order
            self.order_id_counter += 1
        
        return orders 