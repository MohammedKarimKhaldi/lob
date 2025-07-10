"""
Base metrics class for LOB simulation.

This module provides the abstract base class and common functionality
for all market metrics.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BaseMetrics(ABC):
    """Base class for all market metrics."""
    
    def __post_init__(self):
        """Initialize metrics after dataclass creation."""
        pass
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> None:
        """Calculate metrics from data."""
        pass
    
    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of metrics."""
        pass
    
    def reset(self) -> None:
        """Reset metrics state."""
        pass 