"""
Uninformed Trader Agent

A noise trader with no private information that trades randomly.
"""

import numpy as np
import random
from typing import Optional, Dict, Any
from .base import BaseAgent
from ..events import OrderEvent, Event


class UninformedTrader(BaseAgent):
    """
    Uninformed trader (noise trader).
    
    Noise trading with arrival rate λ_U.
    No private information, trades randomly.
    """
    
    def __init__(self, trader_id: str, arrival_rate: float):
        super().__init__(trader_id, arrival_rate)
        self.last_event_time = 0.0
    
    def get_next_event(self, current_time: float) -> Optional[Event]:
        """Generate next order event based on Poisson process."""
        # Generate next arrival time
        interarrival_time = np.random.exponential(1.0 / self.arrival_rate)
        next_event_time = max(self.last_event_time, current_time) + interarrival_time
        
        # Ensure we don't schedule events too far in the future initially
        if self.last_event_time == 0.0:  # First event
            next_event_time = current_time + min(interarrival_time, 1.0)  # Max 1 second delay
        
        if next_event_time <= current_time:
            next_event_time = current_time + 0.1  # Small delay if needed
        
        # Generate order
        order = self._generate_order(next_event_time)
        self.last_event_time = next_event_time
        return order
    
    def _generate_order(self, current_time: float) -> OrderEvent:
        """Generate a random order."""
        side = random.choice(['buy', 'sell'])
        
        # Use more realistic price ranges based on current market conditions
        base_price = 100.0  # Would come from market data
        price_adjustment = random.uniform(-0.01, 0.01)
        price = base_price * (1 + price_adjustment)
        
        quantity = random.randint(10, 100)
        order_type = random.choices(['limit', 'market'], weights=[0.8, 0.2])[0]
        
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
        # Uninformed traders don't use market data for decision making
        pass 