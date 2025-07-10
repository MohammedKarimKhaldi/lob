"""
Mean Reversion Strategy

A mean reversion trading strategy that trades against price trends.
"""

from typing import Dict, List, Any
from .base import BaseStrategy, StrategyConfig
from ..events import OrderEvent


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy implementation."""
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        orders = []
        self.update_market_data(market_data)
        lookback = self.config.lookback_period if hasattr(self.config, 'lookback_period') else 20
        threshold = self.config.mean_reversion_threshold if hasattr(self.config, 'mean_reversion_threshold') else 0.03
        price_history = self.performance.price_history
        
        if len(price_history) < lookback:
            return orders
        
        recent_prices = price_history[-lookback:]
        price_change = recent_prices[-1] - recent_prices[0]
        
        # Mean reversion: sell if price increased, buy if decreased
        if price_change > threshold:
            # Sell signal
            order_id = f"meanrev_sell_{current_time}"
            sell_order = OrderEvent(
                order_id,
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
        elif price_change < -threshold:
            # Buy signal
            order_id = f"meanrev_buy_{current_time}"
            buy_order = OrderEvent(
                order_id,
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
        return orders 