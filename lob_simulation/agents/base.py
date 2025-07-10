"""
Base agent class for LOB simulation.

This module provides the abstract base class and common functionality
for all market agents.
"""

import numpy as np
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from ..events import OrderEvent, CancelEvent, Event


class BaseAgent(ABC):
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