"""
Main simulation engine for the Limit Order Book Simulation.

This module implements the core simulation logic with event-driven architecture,
agent-based modeling, and microsecond precision timing.
"""

import time
import heapq
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from numba import jit

from .orderbook import OrderBook
from .agents import InformedTrader, UninformedTrader, MarketMaker
from .events import OrderEvent, CancelEvent, TradeEvent, Event
from .metrics import MarketMetrics, LiquidityMetrics, ImpactMetrics
from .strategies import StrategyConfig, create_strategy, BaseStrategy


@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    
    # Time settings
    duration: float = 3600.0  # Simulation duration in seconds
    tick_size: float = 0.01   # Minimum price increment
    max_levels: int = 10      # Maximum order book levels to track
    
    # Market parameters
    initial_price: float = 100.0
    volatility: float = 0.02  # Annualized volatility
    mean_reversion: float = 0.1  # Mean reversion speed
    
    # Agent parameters
    num_informed_traders: int = 5
    num_uninformed_traders: int = 20
    num_market_makers: int = 3
    
    # Order flow parameters
    lambda_informed: float = 0.1    # Informed trader arrival rate
    lambda_uninformed: float = 0.5  # Uninformed trader arrival rate
    lambda_market_maker: float = 0.2  # Market maker activity rate
    
    # Price impact parameters
    impact_lambda: float = 0.1      # Linear impact coefficient
    impact_gamma: float = 0.5       # Impact exponent
    temp_decay_tau: float = 300.0   # Temporary impact decay time
    
    # Cancellation parameters
    cancel_half_life: float = 60.0  # Order cancellation half-life
    
    # Market order parameters
    market_order_alpha: float = 1.0
    market_order_s0: float = 0.01   # Spread threshold for market orders


class LimitOrderBookSimulation:
    """
    Main simulation engine for limit order book dynamics.
    
    This class implements an event-driven simulation with microsecond precision,
    featuring agent-based modeling, realistic order flow dynamics, and
    comprehensive market quality metrics.
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the simulation."""
        self.config = config or SimulationConfig()
        
        # Initialize order book
        self.orderbook = OrderBook(
            tick_size=self.config.tick_size,
            max_levels=self.config.max_levels
        )
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Event queue (priority queue for time-based events)
        self.event_queue = []
        self.current_time = 0.0
        
        # Data collection
        self.trades = []
        self.order_events = []
        self.price_history = []
        self.spread_history = []
        self.volume_history = []
        
        # Metrics
        self.metrics = MarketMetrics()
        self.liquidity_metrics = LiquidityMetrics()
        self.impact_metrics = ImpactMetrics()
        
        # Market state
        self.mid_price = self.config.initial_price
        self.best_bid = self.mid_price - self.config.tick_size
        self.best_ask = self.mid_price + self.config.tick_size
        
        # Strategies
        self.strategies = {}
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        
    def _initialize_agents(self) -> Dict[str, List]:
        """Initialize market participants."""
        agents = {
            'informed': [],
            'uninformed': [],
            'market_makers': []
        }
        
        # Create informed traders
        for i in range(self.config.num_informed_traders):
            trader = InformedTrader(
                trader_id=f"informed_{i}",
                arrival_rate=self.config.lambda_informed,
                private_info_prob=0.1
            )
            agents['informed'].append(trader)
        
        # Create uninformed traders
        for i in range(self.config.num_uninformed_traders):
            trader = UninformedTrader(
                trader_id=f"uninformed_{i}",
                arrival_rate=self.config.lambda_uninformed
            )
            agents['uninformed'].append(trader)
        
        # Create market makers
        for i in range(self.config.num_market_makers):
            mm = MarketMaker(
                trader_id=f"mm_{i}",
                arrival_rate=self.config.lambda_market_maker,
                inventory_target=0.0,
                max_inventory=1000
            )
            agents['market_makers'].append(mm)
        
        return agents
    
    def run(self, duration: Optional[float] = None) -> Dict[str, Any]:
        """
        Run the simulation for the specified duration.
        
        Args:
            duration: Simulation duration in seconds (uses config if None)
            
        Returns:
            Dictionary containing simulation results and metrics
        """
        duration = duration or self.config.duration
        self.start_time = time.time()
        
        # Initialize event queue with agent events
        self._schedule_initial_events()
        
        # Main simulation loop
        while self.current_time < duration and self.event_queue:
            # Get next event
            event_time, event = heapq.heappop(self.event_queue)
            self.current_time = event_time
            
            # Process event
            self._process_event(event)
            
            # Schedule next events from agents
            self._schedule_agent_events()
            
            # Record market state
            self._record_market_state()
        
        self.end_time = time.time()
        
        # Calculate final metrics
        self._calculate_final_metrics()
        
        return self.get_results()
    
    def _schedule_initial_events(self):
        """Schedule initial events from all agents."""
        import time
        for agent_type, agent_list in self.agents.items():
            for agent in agent_list:
                next_event = agent.get_next_event(self.current_time)
                if next_event:
                    heapq.heappush(self.event_queue, (next_event.timestamp, time.time(), next_event))
    
    def _schedule_agent_events(self):
        """Schedule next events from agents that just acted."""
        # This is a simplified version - in practice, you'd track which agents
        # need to schedule new events based on their current state
        pass
    
    def _process_event(self, event: Event):
        """Process a single event."""
        if isinstance(event, OrderEvent):
            self._process_order_event(event)
        elif isinstance(event, CancelEvent):
            self._process_cancel_event(event)
        elif isinstance(event, TradeEvent):
            self._process_trade_event(event)
    
    def _process_order_event(self, event: OrderEvent):
        """Process an order event."""
        # Add order to order book
        trades = self.orderbook.add_order(event, current_time=self.current_time)
        
        # Record trades if any
        for trade in trades:
            self.trades.append(trade)
            self._update_price_impact(trade)
            
            # Update strategies with trade
            for strategy in self.strategies.values():
                strategy.process_trade(trade)
        
        # Record order event
        self.order_events.append(event)
    
    def _process_cancel_event(self, event: CancelEvent):
        """Process a cancellation event."""
        self.orderbook.cancel_order(event.order_id)
    
    def _process_trade_event(self, event: TradeEvent):
        """Process a trade event."""
        self.trades.append(event)
        self._update_price_impact(event)
    
    def _update_price_impact(self, trade: TradeEvent):
        """Update price impact based on trade."""
        # Use a more balanced approach for price impact
        # Instead of trying to guess trade direction, use a random walk with mean reversion
        
        # Calculate impact based on trade size (regardless of direction)
        impact_magnitude = self.config.impact_lambda * (trade.quantity ** self.config.impact_gamma)
        
        # Use random direction to avoid systematic bias
        # This simulates the uncertainty in price impact direction
        trade_direction = np.random.choice([-1, 1], p=[0.5, 0.5])
        
        # Calculate temporary impact
        temp_impact = impact_magnitude * trade_direction
        
        # Apply temporary impact
        self.mid_price += temp_impact
        
        # Add mean reversion to prevent drift (reduced strength)
        mean_reversion_force = self.config.mean_reversion * (self.config.initial_price - self.mid_price) * 0.0001
        self.mid_price += mean_reversion_force
        
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 0.001)  # Small random noise
        self.mid_price += noise
        
        # Update best bid/ask
        spread = self.best_ask - self.best_bid
        self.best_bid = self.mid_price - spread / 2
        self.best_ask = self.mid_price + spread / 2
    
    def _record_market_state(self):
        """Record current market state for analysis."""
        self.price_history.append({
            'timestamp': self.current_time,
            'mid_price': self.mid_price,
            'best_bid': self.best_bid,
            'best_ask': self.best_ask
        })
        
        spread = self.best_ask - self.best_bid
        self.spread_history.append({
            'timestamp': self.current_time,
            'spread': spread
        })
        
        # Calculate volume at best bid/ask
        bid_volume = self.orderbook.get_bid_volume()
        ask_volume = self.orderbook.get_ask_volume()
        self.volume_history.append({
            'timestamp': self.current_time,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        })
        
        # Update strategies with market data
        market_data = {
            'mid_price': self.mid_price,
            'best_bid': self.best_bid,
            'best_ask': self.best_ask,
            'spread': spread,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'timestamp': self.current_time
        }
        
        for strategy in self.strategies.values():
            strategy.update_market_data(market_data)
            
            # Generate strategy orders periodically (every 5 seconds)
            if self.current_time % 5.0 < 0.1:  # Every ~5 seconds
                strategy_orders = strategy.generate_orders(self.current_time + 0.1, market_data)
                for i, order in enumerate(strategy_orders):
                    # Add a unique counter to break ties
                    heapq.heappush(self.event_queue, (order.timestamp, time.time() + i * 0.0001, order))
    
    def _calculate_final_metrics(self):
        """Calculate final market metrics."""
        # Convert history to DataFrames
        price_df = pd.DataFrame(self.price_history)
        spread_df = pd.DataFrame(self.spread_history)
        volume_df = pd.DataFrame(self.volume_history)
        trades_df = pd.DataFrame([trade.__dict__ for trade in self.trades])
        
        # Calculate metrics
        self.metrics.calculate(price_df, spread_df, volume_df, trades_df)
        self.liquidity_metrics.calculate(self.orderbook, price_df, volume_df)
        self.impact_metrics.calculate(trades_df, price_df)
    
    def get_results(self) -> Dict[str, Any]:
        """Get simulation results and metrics."""
        return {
            'config': self.config,
            'trades': self.trades,
            'order_events': self.order_events,
            'price_history': self.price_history,
            'spread_history': self.spread_history,
            'volume_history': self.volume_history,
            'metrics': self.metrics.get_summary(),
            'liquidity_metrics': self.liquidity_metrics.get_summary(),
            'impact_metrics': self.impact_metrics.get_summary(),
            'orderbook_state': self.orderbook.get_state(),
            'simulation_time': (self.end_time - self.start_time) if self.end_time and self.start_time else None
        }
    
    def get_orderbook_snapshot(self) -> Dict[str, Any]:
        """Get current order book snapshot."""
        return self.orderbook.get_state()
    
    def add_strategy(self, strategy_name: str, config: StrategyConfig):
        """Add a trading strategy to the simulation."""
        strategy = create_strategy(strategy_name, config)
        self.strategies[strategy_name] = strategy
    
    def get_strategy_performance(self, strategy_name: str) -> Dict[str, Any]:
        """Get performance summary for a specific strategy."""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name].get_performance_summary()
        return {}
    
    def get_all_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance summary for all strategies."""
        return {name: strategy.get_performance_summary() 
                for name, strategy in self.strategies.items()}
    
    def add_custom_event(self, event: Event):
        """Add a custom event to the simulation."""
        heapq.heappush(self.event_queue, (event.timestamp, time.time(), event))
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.orderbook.reset()
        self.event_queue = []
        self.current_time = 0.0
        self.trades = []
        self.order_events = []
        self.price_history = []
        self.spread_history = []
        self.volume_history = []
        self.mid_price = self.config.initial_price
        self.best_bid = self.mid_price - self.config.tick_size
        self.best_ask = self.mid_price + self.config.tick_size 