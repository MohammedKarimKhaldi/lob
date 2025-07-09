"""
Trading Strategies Framework

This module implements various trading strategies for the LOB simulation,
including market making, momentum trading, mean reversion, and arbitrage strategies.
Each strategy tracks its own PnL and performance metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import random

from .events import OrderEvent, CancelEvent, TradeEvent
from .orderbook import OrderBook


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
        if len(self.performance.position_history) > 1000:
            self.performance.position_history.pop(0)
    
    def calculate_metrics(self):
        """Calculate performance metrics."""
        if len(self.performance.pnl_history) > 1:
            # Calculate Sharpe ratio
            returns = np.diff(self.performance.pnl_history)
            if len(returns) > 0 and np.std(returns) > 0:
                self.performance.sharpe_ratio = np.mean(returns) / np.std(returns)
            
            # Calculate win rate
            if self.performance.num_trades > 0:
                self.performance.win_rate = self.performance.num_wins / self.performance.num_trades
            
            # Calculate max drawdown
            peak = np.maximum.accumulate(self.performance.pnl_history)
            drawdown = (self.performance.pnl_history - peak) / peak
            self.performance.max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0
        
        # Calculate fill rate
        if self.performance.num_orders > 0:
            self.performance.fill_rate = self.performance.num_fills / self.performance.num_orders
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        self.calculate_metrics()
        return {
            'strategy_name': self.config.strategy_name,
            'total_pnl': self.performance.total_pnl,
            'realized_pnl': self.performance.realized_pnl,
            'unrealized_pnl': self.performance.unrealized_pnl,
            'current_position': self.performance.current_position,
            'avg_entry_price': self.performance.avg_entry_price,
            'num_trades': self.performance.num_trades,
            'win_rate': self.performance.win_rate,
            'sharpe_ratio': self.performance.sharpe_ratio,
            'max_drawdown': self.performance.max_drawdown,
            'fill_rate': self.performance.fill_rate
        }


class MarketMakingStrategy(BaseStrategy):
    """Market making strategy with inventory management."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.inventory_target = 0
        self.max_inventory = config.max_position
        self.quote_size = 50
        self.spread_multiplier = 1.0
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate market making orders."""
        if not self.is_active:
            return []
        
        orders = []
        
        # Calculate optimal spread based on inventory
        inventory_skew = self.performance.current_position / self.max_inventory
        base_spread = self.config.min_spread
        spread_adjustment = inventory_skew * 0.02  # Adjust spread based on inventory
        optimal_spread = max(self.config.min_spread, 
                           min(self.config.max_spread, base_spread + spread_adjustment))
        
        # Calculate bid and ask prices
        bid_price = self.mid_price - optimal_spread / 2
        ask_price = self.mid_price + optimal_spread / 2
        
        # Place bid order if we can take more inventory
        if self.performance.current_position < self.max_inventory:
            bid_order = OrderEvent(
                order_id=f"mm_bid_{current_time}_{random.randint(1000, 9999)}",
                trader_id=f"mm_{self.config.strategy_name}",
                side='buy',
                price=bid_price,
                quantity=self.quote_size,
                timestamp=current_time,
                order_type='limit'
            )
            orders.append(bid_order)
            self.active_orders[bid_order.order_id] = {
                'side': 'buy',
                'price': bid_price,
                'quantity': self.quote_size
            }
        
        # Place ask order if we can reduce inventory
        if self.performance.current_position > -self.max_inventory:
            ask_order = OrderEvent(
                order_id=f"mm_ask_{current_time}_{random.randint(1000, 9999)}",
                trader_id=f"mm_{self.config.strategy_name}",
                side='sell',
                price=ask_price,
                quantity=self.quote_size,
                timestamp=current_time,
                order_type='limit'
            )
            orders.append(ask_order)
            self.active_orders[ask_order.order_id] = {
                'side': 'sell',
                'price': ask_price,
                'quantity': self.quote_size
            }
        
        self.performance.num_orders += len(orders)
        return orders


class MomentumStrategy(BaseStrategy):
    """Momentum trading strategy."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.lookback_period = config.lookback_period
        self.momentum_threshold = config.momentum_threshold
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate momentum-based orders."""
        if not self.is_active or len(self.performance.price_history) < self.lookback_period:
            return []
        
        orders = []
        
        # Calculate momentum
        recent_prices = self.performance.price_history[-self.lookback_period:]
        if len(recent_prices) >= 2:
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # Generate orders based on momentum
            if momentum > self.momentum_threshold and self.performance.current_position < self.config.max_position:
                # Strong upward momentum - buy
                order = OrderEvent(
                    order_id=f"momentum_buy_{current_time}_{random.randint(1000, 9999)}",
                    trader_id=f"momentum_{self.config.strategy_name}",
                    side='buy',
                    price=self.best_ask,  # Market order
                    quantity=min(50, self.config.max_position - self.performance.current_position),
                    timestamp=current_time,
                    order_type='market'
                )
                orders.append(order)
                self.active_orders[order.order_id] = {
                    'side': 'buy',
                    'price': self.best_ask,
                    'quantity': order.quantity
                }
            
            elif momentum < -self.momentum_threshold and self.performance.current_position > -self.config.max_position:
                # Strong downward momentum - sell
                order = OrderEvent(
                    order_id=f"momentum_sell_{current_time}_{random.randint(1000, 9999)}",
                    trader_id=f"momentum_{self.config.strategy_name}",
                    side='sell',
                    price=self.best_bid,  # Market order
                    quantity=min(50, self.config.max_position + self.performance.current_position),
                    timestamp=current_time,
                    order_type='market'
                )
                orders.append(order)
                self.active_orders[order.order_id] = {
                    'side': 'sell',
                    'price': self.best_bid,
                    'quantity': order.quantity
                }
        
        self.performance.num_orders += len(orders)
        return orders


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.lookback_period = config.lookback_period
        self.reversion_threshold = config.mean_reversion_threshold
        self.mean_price = 100.0
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate mean reversion orders."""
        if not self.is_active or len(self.performance.price_history) < self.lookback_period:
            return []
        
        orders = []
        
        # Calculate mean price
        recent_prices = self.performance.price_history[-self.lookback_period:]
        self.mean_price = np.mean(recent_prices)
        
        # Calculate deviation from mean
        deviation = (self.current_price - self.mean_price) / self.mean_price
        
        # Generate orders based on mean reversion
        if deviation > self.reversion_threshold and self.performance.current_position > -self.config.max_position:
            # Price above mean - sell (expect reversion down)
            order = OrderEvent(
                order_id=f"reversion_sell_{current_time}_{random.randint(1000, 9999)}",
                trader_id=f"reversion_{self.config.strategy_name}",
                side='sell',
                price=self.best_bid,
                quantity=min(50, self.config.max_position + self.performance.current_position),
                timestamp=current_time,
                order_type='market'
            )
            orders.append(order)
            self.active_orders[order.order_id] = {
                'side': 'sell',
                'price': self.best_bid,
                'quantity': order.quantity
            }
        
        elif deviation < -self.reversion_threshold and self.performance.current_position < self.config.max_position:
            # Price below mean - buy (expect reversion up)
            order = OrderEvent(
                order_id=f"reversion_buy_{current_time}_{random.randint(1000, 9999)}",
                trader_id=f"reversion_{self.config.strategy_name}",
                side='buy',
                price=self.best_ask,
                quantity=min(50, self.config.max_position - self.performance.current_position),
                timestamp=current_time,
                order_type='market'
            )
            orders.append(order)
            self.active_orders[order.order_id] = {
                'side': 'buy',
                'price': self.best_ask,
                'quantity': order.quantity
            }
        
        self.performance.num_orders += len(orders)
        return orders


class ArbitrageStrategy(BaseStrategy):
    """Statistical arbitrage strategy."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.arbitrage_threshold = config.arbitrage_threshold
        self.pairs = []  # For pairs trading (if multiple instruments)
    
    def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]:
        """Generate arbitrage orders."""
        if not self.is_active:
            return []
        
        orders = []
        
        # Simple arbitrage based on spread
        if self.spread > self.arbitrage_threshold:
            # Wide spread - place orders on both sides
            if self.performance.current_position < self.config.max_position:
                buy_order = OrderEvent(
                    order_id=f"arb_buy_{current_time}_{random.randint(1000, 9999)}",
                    trader_id=f"arb_{self.config.strategy_name}",
                    side='buy',
                    price=self.best_bid + 0.001,  # Slightly above best bid
                    quantity=min(30, self.config.max_position - self.performance.current_position),
                    timestamp=current_time,
                    order_type='limit'
                )
                orders.append(buy_order)
                self.active_orders[buy_order.order_id] = {
                    'side': 'buy',
                    'price': buy_order.price,
                    'quantity': buy_order.quantity
                }
            
            if self.performance.current_position > -self.config.max_position:
                sell_order = OrderEvent(
                    order_id=f"arb_sell_{current_time}_{random.randint(1000, 9999)}",
                    trader_id=f"arb_{self.config.strategy_name}",
                    side='sell',
                    price=self.best_ask - 0.001,  # Slightly below best ask
                    quantity=min(30, self.config.max_position + self.performance.current_position),
                    timestamp=current_time,
                    order_type='limit'
                )
                orders.append(sell_order)
                self.active_orders[sell_order.order_id] = {
                    'side': 'sell',
                    'price': sell_order.price,
                    'quantity': sell_order.quantity
                }
        
        self.performance.num_orders += len(orders)
        return orders


def create_strategy(strategy_name: str, config: StrategyConfig) -> BaseStrategy:
    """Factory function to create strategies."""
    if strategy_name == "market_making":
        return MarketMakingStrategy(config)
    elif strategy_name == "momentum":
        return MomentumStrategy(config)
    elif strategy_name == "mean_reversion":
        return MeanReversionStrategy(config)
    elif strategy_name == "arbitrage":
        return ArbitrageStrategy(config)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}") 