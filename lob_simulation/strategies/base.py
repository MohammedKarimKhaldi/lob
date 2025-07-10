"""
Base strategy class for LOB simulation.

This module provides the abstract base class and common functionality
for all trading strategies.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ..events import OrderEvent, TradeEvent


@dataclass
class StrategyConfig:
    """Configuration for trading strategies."""
    
    # Strategy parameters
    strategy_name: str = "base"
    initial_capital: float = 100000.0
    max_position: int = 1000
    max_order_size: int = 100
    min_spread: float = 0.01
    max_spread: float = 0.10
    
    # Risk management
    stop_loss: float = 0.05  # 5% stop loss
    take_profit: float = 0.10  # 10% take profit
    max_drawdown: float = 0.20  # 20% max drawdown
    
    # Strategy-specific parameters
    lookback_period: int = 20
    momentum_threshold: float = 0.02
    mean_reversion_threshold: float = 0.03
    arbitrage_threshold: float = 0.005
    tick_size: float = 0.01


@dataclass
class StrategyPerformance:
    """Performance metrics for a trading strategy."""
    
    # PnL metrics
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    # Position metrics
    current_position: int = 0
    avg_entry_price: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    
    # Trade metrics
    num_trades: int = 0
    num_wins: int = 0
    num_losses: int = 0
    
    # Order metrics
    num_orders: int = 0
    num_fills: int = 0
    fill_rate: float = 0.0
    
    # Price history for calculations
    price_history: List[float] = field(default_factory=list)
    pnl_history: List[float] = field(default_factory=list)
    position_history: List[int] = field(default_factory=list)


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.performance = StrategyPerformance()
        self.active_orders = {}  # order_id -> order details
        self.trades = []
        self.order_history = []
        
        # Market state
        self.current_price = 100.0
        self.best_bid = 99.0
        self.best_ask = 101.0
        self.mid_price = 100.0
        self.spread = 2.0
        
        # Strategy state
        self.is_active = True
        self.last_action_time = 0.0
    
    @abstractmethod
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate orders based on current market conditions."""
        pass
    
    def update_market_data(self, market_data: Dict[str, Any]):
        """Update strategy with latest market data."""
        self.current_price = market_data.get('mid_price', self.current_price)
        self.best_bid = market_data.get('best_bid', self.best_bid)
        self.best_ask = market_data.get('best_ask', self.best_ask)
        self.mid_price = market_data.get('mid_price', self.mid_price)
        self.spread = self.best_ask - self.best_bid
        
        # Update price history
        self.performance.price_history.append(self.current_price)
        if len(self.performance.price_history) > 1000:
            self.performance.price_history.pop(0)
    
    def process_trade(self, trade: TradeEvent):
        """Process a trade that affects this strategy."""
        # Determine if this trade was ours
        if trade.buy_order_id in self.active_orders:
            self._process_buy_trade(trade)
        elif trade.sell_order_id in self.active_orders:
            self._process_sell_trade(trade)
    
    def _process_buy_trade(self, trade: TradeEvent):
        """Process a buy trade."""
        # Update position
        old_position = self.performance.current_position
        self.performance.current_position += trade.quantity
        
        # Update average entry price
        if self.performance.current_position != 0:
            total_cost = (old_position * self.performance.avg_entry_price + 
                         trade.quantity * trade.price)
            self.performance.avg_entry_price = total_cost / self.performance.current_position
        
        # Update PnL
        self.performance.realized_pnl += 0  # No realized PnL for buys
        self._update_unrealized_pnl()
        
        # Update trade metrics
        self.performance.num_trades += 1
        self.trades.append(trade)
        
        # Remove filled order
        if trade.buy_order_id in self.active_orders:
            del self.active_orders[trade.buy_order_id]
    
    def _process_sell_trade(self, trade: TradeEvent):
        """Process a sell trade."""
        # Update position
        old_position = self.performance.current_position
        self.performance.current_position -= trade.quantity
        
        # Calculate realized PnL
        if old_position > 0:  # We had a long position
            realized_pnl = (trade.price - self.performance.avg_entry_price) * min(trade.quantity, old_position)
            self.performance.realized_pnl += realized_pnl
            
            if realized_pnl > 0:
                self.performance.num_wins += 1
            else:
                self.performance.num_losses += 1
        
        # Update average entry price
        if self.performance.current_position != 0:
            remaining_position = max(0, old_position - trade.quantity)
            if remaining_position > 0:
                self.performance.avg_entry_price = (remaining_position * self.performance.avg_entry_price) / remaining_position
        
        # Update PnL
        self._update_unrealized_pnl()
        
        # Update trade metrics
        self.performance.num_trades += 1
        self.trades.append(trade)
        
        # Remove filled order
        if trade.sell_order_id in self.active_orders:
            del self.active_orders[trade.sell_order_id]
    
    def _update_unrealized_pnl(self):
        """Update unrealized PnL based on current position and price."""
        if self.performance.current_position != 0:
            self.performance.unrealized_pnl = (
                self.performance.current_position * 
                (self.current_price - self.performance.avg_entry_price)
            )
        else:
            self.performance.unrealized_pnl = 0.0
        
        self.performance.total_pnl = self.performance.realized_pnl + self.performance.unrealized_pnl
        
        # Update PnL history
        self.performance.pnl_history.append(self.performance.total_pnl)
        if len(self.performance.pnl_history) > 1000:
            self.performance.pnl_history.pop(0)
        
        # Update position history
        self.performance.position_history.append(self.performance.current_position)
    
    def calculate_metrics(self):
        """Calculate performance metrics."""
        if len(self.performance.pnl_history) < 2:
            return
        
        # Calculate Sharpe ratio
        returns = np.diff(self.performance.pnl_history)
        if len(returns) > 0 and np.std(returns) > 0:
            self.performance.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # Calculate win rate
        if self.performance.num_trades > 0:
            self.performance.win_rate = self.performance.num_wins / self.performance.num_trades
        
        # Calculate max drawdown
        if len(self.performance.pnl_history) > 0:
            peak = np.maximum.accumulate(self.performance.pnl_history)
            drawdown = (self.performance.pnl_history - peak) / peak
            self.performance.max_drawdown = np.min(drawdown)
        
        # Calculate fill rate
        if self.performance.num_orders > 0:
            self.performance.fill_rate = self.performance.num_fills / self.performance.num_orders
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        self.calculate_metrics()
        
        return {
            'strategy_name': self.config.strategy_name,
            'total_pnl': self.performance.total_pnl,
            'realized_pnl': self.performance.realized_pnl,
            'unrealized_pnl': self.performance.unrealized_pnl,
            'current_position': self.performance.current_position,
            'avg_entry_price': self.performance.avg_entry_price,
            'max_drawdown': self.performance.max_drawdown,
            'sharpe_ratio': self.performance.sharpe_ratio,
            'win_rate': self.performance.win_rate,
            'num_trades': self.performance.num_trades,
            'num_wins': self.performance.num_wins,
            'num_losses': self.performance.num_losses,
            'num_orders': self.performance.num_orders,
            'num_fills': self.performance.num_fills,
            'fill_rate': self.performance.fill_rate
        } 