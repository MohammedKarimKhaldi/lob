"""
Limit Order Book Simulation Package

A comprehensive market microstructure modeling framework for simulating
limit order book dynamics, analyzing market making strategies, and studying
price impact and liquidity provision mechanisms.
"""

__version__ = "1.0.0"
__author__ = "Limit Order Book Simulation Team"
__email__ = "contact@lob-simulation.com"

from .core.simulation import LimitOrderBookSimulation, SimulationConfig
from .orderbook import OrderBook
from .agents import InformedTrader, UninformedTrader, MarketMaker
from .events import OrderEvent, CancelEvent, TradeEvent
from .metrics import MarketMetrics, LiquidityMetrics, ImpactMetrics
from .strategies import (
    StrategyConfig, BaseStrategy, MarketMakingStrategy, 
    MomentumStrategy, MeanReversionStrategy, ArbitrageStrategy,
    create_strategy
)

__all__ = [
    "LimitOrderBookSimulation",
    "SimulationConfig",
    "OrderBook",
    "InformedTrader",
    "UninformedTrader", 
    "MarketMaker",
    "OrderEvent",
    "CancelEvent",
    "TradeEvent",
    "MarketMetrics",
    "LiquidityMetrics",
    "ImpactMetrics",
    "StrategyConfig",
    "BaseStrategy",
    "MarketMakingStrategy",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "ArbitrageStrategy",
    "create_strategy",
] 