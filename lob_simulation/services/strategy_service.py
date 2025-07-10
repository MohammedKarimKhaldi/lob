"""
Strategy Service

This service manages trading strategies and their lifecycle.
"""

from typing import Dict, Any, List


class StrategyService:
    """Service for managing trading strategies."""
    
    def __init__(self):
        pass
    
    def list_strategies(self) -> List[str]:
        """List available strategies."""
        return ["market_making", "momentum", "mean_reversion", "arbitrage"]
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get default configuration for a strategy."""
        return {"strategy_name": strategy_name} 