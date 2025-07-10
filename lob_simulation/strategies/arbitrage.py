"""
Arbitrage Strategy

An arbitrage trading strategy that exploits price differences.
"""

from typing import Dict, List, Any
from .base import BaseStrategy, StrategyConfig
from ..events import OrderEvent


class ArbitrageStrategy(BaseStrategy):
    """Arbitrage strategy implementation."""
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        orders = []
        self.update_market_data(market_data)
        threshold = self.config.arbitrage_threshold if hasattr(self.config, 'arbitrage_threshold') else 0.005
        spread = self.spread
        
        # If spread is wide enough, try to capture it
        if spread > threshold:
            # Buy at bid
            buy_order = OrderEvent(
                f"arb_buy_{current_time}",
                self.config.strategy_name,
                "buy",
                self.best_bid + self.config.tick_size,
                min(self.config.max_order_size, self.config.max_position - self.performance.current_position),
                current_time,
                "limit"
            )
            if buy_order.quantity > 0:
                orders.append(buy_order)
                self.active_orders[buy_order.order_id] = buy_order
            # Sell at ask
            sell_order = OrderEvent(
                f"arb_sell_{current_time}",
                self.config.strategy_name,
                "sell",
                self.best_ask - self.config.tick_size,
                min(self.config.max_order_size, self.config.max_position + self.performance.current_position),
                current_time,
                "limit"
            )
            if sell_order.quantity > 0:
                orders.append(sell_order)
                self.active_orders[sell_order.order_id] = sell_order
        return orders 