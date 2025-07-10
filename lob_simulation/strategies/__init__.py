"""
Strategy plugin system for LOB simulation.

This module provides a plugin architecture for trading strategies,
allowing easy addition of new strategies without modifying core code.
"""

from typing import Dict, Type, Optional
from .base import BaseStrategy
from .market_making import MarketMakingStrategy
from .momentum import MomentumStrategy
from .mean_reversion import MeanReversionStrategy
from .arbitrage import ArbitrageStrategy


class StrategyRegistry:
    """Registry for trading strategy plugins."""
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register built-in strategies."""
        self.register('market_making', MarketMakingStrategy)
        self.register('momentum', MomentumStrategy)
        self.register('mean_reversion', MeanReversionStrategy)
        self.register('arbitrage', ArbitrageStrategy)
    
    def register(self, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """Register a new strategy."""
        self._strategies[name] = strategy_class
    
    def get(self, name: str) -> Optional[Type[BaseStrategy]]:
        """Get a strategy class by name."""
        return self._strategies.get(name)
    
    def list_available(self) -> list[str]:
        """List all available strategy names."""
        return list(self._strategies.keys())
    
    def create(self, name: str, config: Dict) -> BaseStrategy:
        """Create a strategy instance."""
        strategy_class = self.get(name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {name}")
        return strategy_class(config)


# Global registry instance
strategy_registry = StrategyRegistry()


def register_strategy(name: str, strategy_class: Type[BaseStrategy]) -> None:
    """Register a strategy globally."""
    strategy_registry.register(name, strategy_class)


def get_strategy(name: str) -> Optional[Type[BaseStrategy]]:
    """Get a strategy class by name."""
    return strategy_registry.get(name)


def create_strategy(name: str, config: Dict) -> BaseStrategy:
    """Create a strategy instance."""
    return strategy_registry.create(name, config)


def list_strategies() -> list[str]:
    """List all available strategies."""
    return strategy_registry.list_available()


# Convenience imports
from .base import BaseStrategy, StrategyConfig, StrategyPerformance 