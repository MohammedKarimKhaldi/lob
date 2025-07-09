"""
Configuration settings for the LOB simulation.
Centralized configuration management for all simulation parameters.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters."""
    initial_price: float = 100.0
    tick_size: float = 0.01
    max_orders: int = 10000
    simulation_duration: float = 3600.0  # 1 hour
    time_step: float = 0.1
    random_seed: Optional[int] = None


@dataclass
class AgentConfig:
    """Configuration for agent parameters."""
    informed_trader_lambda: float = 0.1
    uninformed_trader_lambda: float = 0.5
    market_maker_count: int = 3
    initial_capital: float = 100000.0
    max_position: int = 1000


@dataclass
class OrderBookConfig:
    """Configuration for order book parameters."""
    max_levels: int = 10
    min_spread: float = 0.01
    max_spread: float = 1.0
    order_arrival_rate: float = 1.0
    cancellation_rate: float = 0.1


@dataclass
class StrategyConfig:
    """Configuration for trading strategies."""
    market_making_spread: float = 0.02
    momentum_window: int = 20
    mean_reversion_threshold: float = 0.05
    arbitrage_threshold: float = 0.01
    risk_free_rate: float = 0.02


@dataclass
class WebConfig:
    """Configuration for web interface."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = True
    websocket_ping_interval: int = 25
    websocket_ping_timeout: int = 10


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


class ConfigManager:
    """Centralized configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.simulation = SimulationConfig()
        self.agent = AgentConfig()
        self.orderbook = OrderBookConfig()
        self.strategy = StrategyConfig()
        self.web = WebConfig()
        self.logging = LoggingConfig()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update each config section
            for section, data in config_data.items():
                if hasattr(self, section):
                    section_config = getattr(self, section)
                    for key, value in data.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to JSON file."""
        config_data = {
            'simulation': self.simulation.__dict__,
            'agent': self.agent.__dict__,
            'orderbook': self.orderbook.__dict__,
            'strategy': self.strategy.__dict__,
            'web': self.web.__dict__,
            'logging': self.logging.__dict__
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config file {config_file}: {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            'simulation': self.simulation.__dict__,
            'agent': self.agent.__dict__,
            'orderbook': self.orderbook.__dict__,
            'strategy': self.strategy.__dict__,
            'web': self.web.__dict__,
            'logging': self.logging.__dict__
        }
    
    def update_config(self, section: str, **kwargs) -> None:
        """Update configuration for a specific section."""
        if hasattr(self, section):
            section_config = getattr(self, section)
            for key, value in kwargs.items():
                if hasattr(section_config, key):
                    setattr(section_config, key, value)


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config


def load_config_from_env() -> None:
    """Load configuration from environment variables."""
    # Simulation config
    initial_price = os.getenv('LOB_INITIAL_PRICE')
    if initial_price:
        config.simulation.initial_price = float(initial_price)
    
    simulation_duration = os.getenv('LOB_SIMULATION_DURATION')
    if simulation_duration:
        config.simulation.simulation_duration = float(simulation_duration)
    
    # Web config
    host = os.getenv('LOB_HOST')
    if host:
        config.web.host = host
    
    port = os.getenv('LOB_PORT')
    if port:
        config.web.port = int(port)
    
    debug = os.getenv('LOB_DEBUG')
    if debug:
        config.web.debug = debug.lower() == 'true'
    
    # Logging config
    log_level = os.getenv('LOB_LOG_LEVEL')
    if log_level:
        config.logging.level = log_level
    
    log_file = os.getenv('LOB_LOG_FILE')
    if log_file:
        config.logging.file = log_file 