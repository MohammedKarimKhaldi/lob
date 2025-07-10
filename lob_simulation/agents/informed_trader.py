"""
Informed Trader Agent

An informed trader with private information that follows Poisson process.
"""

import numpy as np
import random
from typing import Optional, Dict, Any
from .base import BaseAgent
from ..events import OrderEvent, Event


class InformedTrader(BaseAgent):
    """
    Informed trader with private information.
    
    Private information arrival follows Poisson process λ_I.
    When informed, trader has better price prediction.
    """
    
    def __init__(self, trader_id: str, arrival_rate: float, private_info_prob: float = 0.1):
        super().__init__(trader_id, arrival_rate)
        self.private_info_prob = private_info_prob
        self.has_private_info = False
        self.private_info_direction = 0  # -1 for bearish, 1 for bullish
        self.private_info_strength = 0.0
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
        """Generate an order based on current market conditions and private info."""
        # Determine if we have private information
        if random.random() < self.private_info_prob:
            self.has_private_info = True
            self.private_info_direction = random.choice([-1, 1])
            self.private_info_strength = random.uniform(0.01, 0.05)
        
        # Generate order parameters
        side = self._choose_side()
        price = self._choose_price(side)
        quantity = self._choose_quantity()
        order_type = self._choose_order_type()
        
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
    
    def _choose_side(self) -> str:
        """Choose order side based on private information."""
        if self.has_private_info:
            if self.private_info_direction > 0:
                return 'buy'
            else:
                return 'sell'
        else:
            return random.choice(['buy', 'sell'])
    
    def _choose_price(self, side: str) -> float:
        """Choose order price based on side and private information."""
        # Base price (would come from market data in real implementation)
        base_price = 100.0
        
        if self.has_private_info:
            # Informed traders place orders more aggressively
            if side == 'buy':
                price_adjustment = self.private_info_strength
            else:
                price_adjustment = -self.private_info_strength
        else:
            # Random price adjustment
            price_adjustment = random.uniform(-0.02, 0.02)
        
        return base_price * (1 + price_adjustment)
    
    def _choose_quantity(self) -> int:
        """Choose order quantity."""
        if self.has_private_info:
            # Informed traders place larger orders
            return random.randint(100, 500)
        else:
            return random.randint(10, 100)
    
    def _choose_order_type(self) -> str:
        """Choose order type."""
        if self.has_private_info:
            # Informed traders more likely to use market orders
            return random.choices(['limit', 'market'], weights=[0.3, 0.7])[0]
        else:
            return random.choices(['limit', 'market'], weights=[0.7, 0.3])[0]
    
    def process_market_data(self, market_data: Dict[str, Any]):
        """Process market data updates."""
        # Update private information based on market movements
        if self.has_private_info:
            # Private information becomes less valuable over time
            self.private_info_strength *= 0.99
            if self.private_info_strength < 0.001:
                self.has_private_info = False 