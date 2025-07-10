"""
Agent plugin system for LOB simulation.

This module provides a plugin architecture for market agents,
allowing easy addition of new agent types without modifying core code.
"""

from typing import Dict, Type, Optional
from .base import BaseAgent
from .informed_trader import InformedTrader
from .uninformed_trader import UninformedTrader
from .market_maker import MarketMaker


class AgentRegistry:
    """Registry for market agent plugins."""
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register built-in agents."""
        self.register('informed', InformedTrader)
        self.register('uninformed', UninformedTrader)
        self.register('market_maker', MarketMaker)
    
    def register(self, name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type."""
        self._agents[name] = agent_class
    
    def get(self, name: str) -> Optional[Type[BaseAgent]]:
        """Get an agent class by name."""
        return self._agents.get(name)
    
    def list_available(self) -> list[str]:
        """List all available agent names."""
        return list(self._agents.keys())
    
    def create(self, name: str, **kwargs) -> BaseAgent:
        """Create an agent instance."""
        agent_class = self.get(name)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {name}")
        return agent_class(**kwargs)


# Global registry instance
agent_registry = AgentRegistry()


def register_agent(name: str, agent_class: Type[BaseAgent]) -> None:
    """Register an agent globally."""
    agent_registry.register(name, agent_class)


def get_agent(name: str) -> Optional[Type[BaseAgent]]:
    """Get an agent class by name."""
    return agent_registry.get(name)


def create_agent(name: str, **kwargs) -> BaseAgent:
    """Create an agent instance."""
    return agent_registry.create(name, **kwargs)


def list_agents() -> list[str]:
    """List all available agents."""
    return agent_registry.list_available()


# Convenience imports
from .base import BaseAgent 