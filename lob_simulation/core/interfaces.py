"""
Abstract interfaces for the LOB simulation framework.

This module defines the core interfaces that enable loose coupling
and dependency inversion throughout the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from dataclasses import dataclass


class MarketDataProvider(Protocol):
    """Protocol for market data providers."""
    
    def get_order_book(self) -> Dict[str, Any]:
        """Get current order book state."""
        ...
    
    def get_price_history(self) -> List[Dict[str, Any]]:
        """Get price history."""
        ...
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        ...


class EventProcessor(ABC):
    """Abstract interface for event processors."""
    
    @abstractmethod
    def process_event(self, event: Any) -> None:
        """Process a single event."""
        pass
    
    @abstractmethod
    def can_process(self, event_type: str) -> bool:
        """Check if this processor can handle the given event type."""
        pass


class Strategy(ABC):
    """Abstract interface for trading strategies."""
    
    @abstractmethod
    def generate_orders(self, market_data: Dict[str, Any]) -> List[Any]:
        """Generate orders based on market data."""
        pass
    
    @abstractmethod
    def update_market_data(self, market_data: Dict[str, Any]) -> None:
        """Update strategy with latest market data."""
        pass
    
    @abstractmethod
    def process_trade(self, trade: Any) -> None:
        """Process a trade that affects this strategy."""
        pass
    
    @abstractmethod
    def get_performance(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        pass


class Agent(ABC):
    """Abstract interface for market agents."""
    
    @abstractmethod
    def get_next_event(self, current_time: float) -> Optional[Any]:
        """Get the next event from this agent."""
        pass
    
    @abstractmethod
    def process_market_update(self, market_data: Dict[str, Any]) -> None:
        """Process market updates."""
        pass


class MetricsCalculator(ABC):
    """Abstract interface for metrics calculation."""
    
    @abstractmethod
    def calculate_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics from market data."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset metrics state."""
        pass


class DataRepository(ABC):
    """Abstract interface for data persistence."""
    
    @abstractmethod
    def save_trade(self, trade: Any) -> None:
        """Save a trade to storage."""
        pass
    
    @abstractmethod
    def save_order(self, order: Any) -> None:
        """Save an order to storage."""
        pass
    
    @abstractmethod
    def get_trades(self, limit: Optional[int] = None) -> List[Any]:
        """Get trades from storage."""
        pass
    
    @abstractmethod
    def get_orders(self, limit: Optional[int] = None) -> List[Any]:
        """Get orders from storage."""
        pass


class SimulationEngine(ABC):
    """Abstract interface for simulation engines."""
    
    @abstractmethod
    def start(self, config: Dict[str, Any]) -> None:
        """Start the simulation."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the simulation."""
        pass
    
    @abstractmethod
    def step(self, max_events: int = 10) -> None:
        """Run simulation for one step."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get simulation status."""
        pass
    
    @abstractmethod
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data."""
        pass


@dataclass
class SimulationConfig:
    """Configuration for simulation components."""
    
    # Core settings
    duration: float = 3600.0
    tick_size: float = 0.01
    max_levels: int = 10
    initial_price: float = 100.0
    
    # Agent settings
    num_informed_traders: int = 5
    num_uninformed_traders: int = 20
    num_market_makers: int = 3
    
    # Strategy settings
    strategies: Dict[str, Dict[str, Any]] = None  # type: ignore
    
    # Performance settings
    refresh_rate: float = 1.0
    
    def __post_init__(self):
        if self.strategies is None:
            self.strategies = {}


class SimulationFactory(ABC):
    """Abstract factory for creating simulation components."""
    
    @abstractmethod
    def create_engine(self, config: SimulationConfig) -> SimulationEngine:
        """Create a simulation engine."""
        pass
    
    @abstractmethod
    def create_strategy(self, strategy_type: str, config: Dict[str, Any]) -> Strategy:
        """Create a trading strategy."""
        pass
    
    @abstractmethod
    def create_agent(self, agent_type: str, config: Dict[str, Any]) -> Agent:
        """Create a market agent."""
        pass
    
    @abstractmethod
    def create_metrics_calculator(self) -> MetricsCalculator:
        """Create a metrics calculator."""
        pass
    
    @abstractmethod
    def create_data_repository(self) -> DataRepository:
        """Create a data repository."""
        pass 