"""
Market Maker Agent

A market maker that provides liquidity by maintaining bid-ask spreads.
"""

import numpy as np
import random
from typing import Optional, Dict, Any
from .base import BaseAgent
from ..events import OrderEvent, CancelEvent, Event


class MarketMaker(BaseAgent):
    """
    Market maker agent.
    
    Provides liquidity by maintaining bid-ask spreads.
    Manages inventory and adjusts quotes based on market conditions.
    """
    
    def __init__(self, trader_id: str, arrival_rate: float, 
                 inventory_target: float = 0.0, max_inventory: int = 1000):
        super().__init__(trader_id, arrival_rate)
        self.inventory_target = inventory_target
        self.max_inventory = max_inventory
        self.bid_price = 99.0
        self.ask_price = 101.0
        self.spread = 2.0
        self.last_event_time = 0.0
        self.quote_update_interval = 1.0  # Update quotes every second
    
    def get_next_event(self, current_time: float) -> Optional[Event]:
        """Generate next market making event."""
        # Generate next arrival time
        interarrival_time = np.random.exponential(1.0 / self.arrival_rate)
        next_event_time = max(self.last_event_time, current_time) + interarrival_time
        
        # Ensure we don't schedule events too far in the future initially
        if self.last_event_time == 0.0:  # First event
            next_event_time = current_time + min(interarrival_time, 0.5)  # Max 0.5 second delay
        
        if next_event_time <= current_time:
            next_event_time = current_time + 0.1  # Small delay if needed
        
        # Update quotes and generate order
        self._update_quotes()
        order = self._generate_market_making_order(next_event_time)
        self.last_event_time = next_event_time
        
        return order
    
    def _update_quotes(self):
        """Update bid and ask prices based on inventory and market conditions."""
        # Base mid price (would come from market data)
        mid_price = 100.0
        
        # Adjust spread based on inventory
        inventory_skew = self.inventory / self.max_inventory
        spread_adjustment = inventory_skew * 0.5  # Wider spread when inventory is skewed
        
        # Base spread
        base_spread = 0.02  # 2 cents
        self.spread = base_spread + abs(spread_adjustment)
        
        # Set bid and ask prices
        self.bid_price = mid_price - self.spread / 2
        self.ask_price = mid_price + self.spread / 2
        
        # Adjust for inventory management
        if self.inventory > self.inventory_target:
            # Long inventory, lower ask to encourage selling
            self.ask_price -= 0.001
        elif self.inventory < self.inventory_target:
            # Short inventory, raise bid to encourage buying
            self.bid_price += 0.001
    
    def _generate_market_making_order(self, current_time: float) -> Optional[OrderEvent]:
        """Generate a market making order."""
        # Determine which side to place order on
        if self.inventory < self.inventory_target:
            # Need to buy
            side = 'buy'
            price = self.bid_price
        elif self.inventory > self.inventory_target:
            # Need to sell
            side = 'sell'
            price = self.ask_price
        else:
            # Balanced inventory, randomly choose side
            side = random.choice(['buy', 'sell'])
            price = self.bid_price if side == 'buy' else self.ask_price
        
        # Determine quantity based on inventory management
        max_quantity = min(50, abs(self.inventory_target - self.inventory))
        if max_quantity <= 0:
            max_quantity = 10  # Minimum order size
        
        quantity = random.randint(10, int(max_quantity))
        order_type = 'limit'
        
        order_id = f"{self.trader_id}_order_{len(self.active_orders)}"
        
        return OrderEvent(
            order_id=order_id,
            trader_id=self.trader_id,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=current_time,
            order_type=order_type
        )
    
    def process_market_data(self, market_data: Dict[str, Any]):
        """Process market data updates."""
        # Update quotes based on market data
        if 'mid_price' in market_data:
            mid_price = market_data['mid_price']
            # Adjust our quotes to stay competitive
            self.bid_price = mid_price - self.spread / 2
            self.ask_price = mid_price + self.spread / 2
    
    def cancel_stale_orders(self, current_time: float) -> Optional[CancelEvent]:
        """Cancel stale orders."""
        # Simple implementation - cancel orders older than 60 seconds
        for order_id, order in self.active_orders.items():
            if current_time - order.timestamp > 60.0:
                return CancelEvent(
                    order_id=order_id,
                    trader_id=self.trader_id,
                    timestamp=current_time
                )
        return None 