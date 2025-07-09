"""
Agent-Based Modeling Framework

This module implements different types of market participants:
- Informed Traders: Private information arrival follows Poisson process λ_I
- Uninformed Traders: Noise trading with arrival rate λ_U  
- Market Makers: Bid-ask spread optimization with inventory management
"""

import numpy as np
import random
from typing import Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .events import OrderEvent, CancelEvent, Event


class Agent(ABC):
    """Base class for all market participants."""
    
    def __init__(self, trader_id: str, arrival_rate: float):
        self.trader_id = trader_id
        self.arrival_rate = arrival_rate
        self.active_orders = {}  # order_id -> order details
        self.inventory = 0
        self.cash = 100000.0  # Starting cash
        self.pnl = 0.0
    
    @abstractmethod
    def get_next_event(self, current_time: float) -> Optional[Event]:
        """Generate the next event for this agent."""
        pass
    
    @abstractmethod
    def process_market_data(self, market_data: Dict[str, Any]):
        """Process market data updates."""
        pass
    
    def update_pnl(self, trade_price: float, trade_quantity: int, side: str):
        """Update P&L based on trade."""
        if side == 'buy':
            self.inventory += trade_quantity
            self.cash -= trade_price * trade_quantity
        else:
            self.inventory -= trade_quantity
            self.cash += trade_price * trade_quantity
        
        # Calculate unrealized P&L (simplified)
        self.pnl = self.cash + self.inventory * trade_price - 100000.0


class InformedTrader(Agent):
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
        if next_event_time <= current_time:
            next_event_time = current_time + interarrival_time
        # Generate order
        order = self._generate_order(next_event_time)
        self.last_event_time = next_event_time  # Use the calculated next event time
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


class UninformedTrader(Agent):
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
        if next_event_time <= current_time:
            next_event_time = current_time + interarrival_time
        # Generate order
        order = self._generate_order(next_event_time)
        self.last_event_time = next_event_time  # Use the calculated next event time
        return order
    
    def _generate_order(self, current_time: float) -> OrderEvent:
        """Generate a random order."""
        side = random.choice(['buy', 'sell'])
        
        # Use more realistic price ranges based on current market conditions
        # This helps create more balanced order flow
        base_price = 100.0
        price_range = 0.05  # 5% range
        
        if side == 'buy':
            # Buy orders tend to be at or below market price
            price = random.uniform(base_price * (1 - price_range), base_price * (1 + 0.02))
        else:
            # Sell orders tend to be at or above market price
            price = random.uniform(base_price * (1 - 0.02), base_price * (1 + price_range))
        
        quantity = random.randint(5, 50)
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
        """Process market data updates (no special processing for uninformed traders)."""
        pass


class MarketMaker(Agent):
    """
    Market maker with bid-ask spread optimization and inventory management.
    
    Maintains bid and ask quotes, manages inventory risk,
    and adjusts spreads based on market conditions.
    """
    
    def __init__(self, trader_id: str, arrival_rate: float, 
                 inventory_target: float = 0.0, max_inventory: int = 1000):
        super().__init__(trader_id, arrival_rate)
        self.inventory_target = inventory_target
        self.max_inventory = max_inventory
        self.spread_multiplier = 1.0
        self.last_event_time = 0.0
        self.bid_price = 99.0
        self.ask_price = 101.0
        self.quote_size = 100
    
    def get_next_event(self, current_time: float) -> Optional[Event]:
        """Generate next market making event."""
        # Generate next arrival time
        interarrival_time = np.random.exponential(1.0 / self.arrival_rate)
        next_event_time = max(self.last_event_time, current_time) + interarrival_time
        if next_event_time <= current_time:
            next_event_time = current_time + interarrival_time
        # Update quotes and potentially place orders
        self._update_quotes()
        order = self._generate_market_making_order(next_event_time)
        self.last_event_time = next_event_time
        return order
    
    def _update_quotes(self):
        """Update bid and ask quotes based on inventory and market conditions."""
        # Base spread
        base_spread = 0.02  # 2 cents
        
        # Adjust spread based on inventory
        inventory_skew = (self.inventory - self.inventory_target) / self.max_inventory
        spread_adjustment = inventory_skew * 0.01  # 1 cent per max inventory
        
        # Calculate new spread
        new_spread = base_spread + spread_adjustment
        new_spread = max(0.01, min(0.10, new_spread))  # Clamp between 1-10 cents
        
        # Update prices based on current market mid price
        # Use a more dynamic approach - market makers should follow the market
        mid_price = 100.0  # Default, but should be updated from market data
        self.bid_price = mid_price - new_spread / 2
        self.ask_price = mid_price + new_spread / 2
    
    def _generate_market_making_order(self, current_time: float) -> Optional[OrderEvent]:
        """Generate market making orders based on current quotes."""
        # Decide whether to place bid, ask, or both
        action = random.choice(['bid', 'ask', 'both'])
        
        if action == 'bid' or action == 'both':
            if self.inventory < self.max_inventory:
                order_id = f"{self.trader_id}_bid_{len(self.active_orders)}"
                return OrderEvent(
                    order_id=order_id,
                    trader_id=self.trader_id,
                    side='buy',
                    price=self.bid_price,
                    quantity=self.quote_size,
                    timestamp=current_time,
                    order_type='limit'
                )
        
        if action == 'ask' or action == 'both':
            if self.inventory > -self.max_inventory:
                order_id = f"{self.trader_id}_ask_{len(self.active_orders)}"
                return OrderEvent(
                    order_id=order_id,
                    trader_id=self.trader_id,
                    side='sell',
                    price=self.ask_price,
                    quantity=self.quote_size,
                    timestamp=current_time,
                    order_type='limit'
                )
        
        return None
    
    def process_market_data(self, market_data: Dict[str, Any]):
        """Process market data updates."""
        # Update quotes based on market conditions
        if 'best_bid' in market_data and 'best_ask' in market_data:
            market_spread = market_data['best_ask'] - market_data['best_bid']
            
            # Adjust our spread based on market spread
            if market_spread > 0:
                self.spread_multiplier = min(2.0, max(0.5, market_spread / 0.02))
    
    def cancel_stale_orders(self, current_time: float) -> Optional[CancelEvent]:
        """Cancel stale orders to manage inventory."""
        # Simple strategy: cancel orders if inventory is too skewed
        if abs(self.inventory) > self.max_inventory * 0.8:
            # Cancel orders on the side that would increase inventory skew
            if self.inventory > 0:
                # Cancel buy orders
                for order_id in list(self.active_orders.keys()):
                    if self.active_orders[order_id]['side'] == 'buy':
                        return CancelEvent(order_id, self.trader_id, current_time)
            else:
                # Cancel sell orders
                for order_id in list(self.active_orders.keys()):
                    if self.active_orders[order_id]['side'] == 'sell':
                        return CancelEvent(order_id, self.trader_id, current_time)
        
        return None 