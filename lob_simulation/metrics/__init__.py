"""
Metrics plugin system for LOB simulation.

This module provides a plugin architecture for market metrics,
allowing easy addition of new metric types without modifying core code.
"""

from typing import Dict, Type, Optional
from .base import BaseMetrics
from .market_metrics import MarketMetrics
from .liquidity_metrics import LiquidityMetrics
from .impact_metrics import ImpactMetrics


class MetricsRegistry:
    """Registry for metrics plugins."""
    
    def __init__(self):
        self._metrics: Dict[str, Type[BaseMetrics]] = {}
        self._register_default_metrics()
    
    def _register_default_metrics(self):
        """Register built-in metrics."""
        self.register('market', MarketMetrics)
        self.register('liquidity', LiquidityMetrics)
        self.register('impact', ImpactMetrics)
    
    def register(self, name: str, metrics_class: Type[BaseMetrics]) -> None:
        """Register a new metrics type."""
        self._metrics[name] = metrics_class
    
    def get(self, name: str) -> Optional[Type[BaseMetrics]]:
        """Get a metrics class by name."""
        return self._metrics.get(name)
    
    def list_available(self) -> list[str]:
        """List all available metrics names."""
        return list(self._metrics.keys())
    
    def create(self, name: str, **kwargs) -> BaseMetrics:
        """Create a metrics instance."""
        metrics_class = self.get(name)
        if not metrics_class:
            raise ValueError(f"Unknown metrics type: {name}")
        return metrics_class(**kwargs)


# Global registry instance
metrics_registry = MetricsRegistry()


def register_metrics(name: str, metrics_class: Type[BaseMetrics]) -> None:
    """Register metrics globally."""
    metrics_registry.register(name, metrics_class)


def get_metrics(name: str) -> Optional[Type[BaseMetrics]]:
    """Get a metrics class by name."""
    return metrics_registry.get(name)


def create_metrics(name: str, **kwargs) -> BaseMetrics:
    """Create a metrics instance."""
    return metrics_registry.create(name, **kwargs)


def list_metrics() -> list[str]:
    """List all available metrics."""
    return metrics_registry.list_available()


# Convenience imports
from .base import BaseMetrics 