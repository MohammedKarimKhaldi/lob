"""
Unit tests for the configuration module.
"""

import unittest
import tempfile
import json
import os
from unittest.mock import patch

from config.settings import (
    SimulationConfig, AgentConfig, OrderBookConfig, 
    StrategyConfig, WebConfig, LoggingConfig, ConfigManager
)


class TestSimulationConfig(unittest.TestCase):
    """Test SimulationConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = SimulationConfig()
        
        self.assertEqual(config.initial_price, 100.0)
        self.assertEqual(config.tick_size, 0.01)
        self.assertEqual(config.max_orders, 10000)
        self.assertEqual(config.simulation_duration, 3600.0)
        self.assertEqual(config.time_step, 0.1)
        self.assertIsNone(config.random_seed)
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = SimulationConfig(
            initial_price=150.0,
            tick_size=0.05,
            max_orders=5000,
            simulation_duration=1800.0,
            time_step=0.2,
            random_seed=42
        )
        
        self.assertEqual(config.initial_price, 150.0)
        self.assertEqual(config.tick_size, 0.05)
        self.assertEqual(config.max_orders, 5000)
        self.assertEqual(config.simulation_duration, 1800.0)
        self.assertEqual(config.time_step, 0.2)
        self.assertEqual(config.random_seed, 42)


class TestAgentConfig(unittest.TestCase):
    """Test AgentConfig class."""
    
    def test_default_values(self):
        """Test default agent configuration values."""
        config = AgentConfig()
        
        self.assertEqual(config.informed_trader_lambda, 0.1)
        self.assertEqual(config.uninformed_trader_lambda, 0.5)
        self.assertEqual(config.market_maker_count, 3)
        self.assertEqual(config.initial_capital, 100000.0)
        self.assertEqual(config.max_position, 1000)
    
    def test_custom_values(self):
        """Test custom agent configuration values."""
        config = AgentConfig(
            informed_trader_lambda=0.2,
            uninformed_trader_lambda=0.8,
            market_maker_count=5,
            initial_capital=200000.0,
            max_position=2000
        )
        
        self.assertEqual(config.informed_trader_lambda, 0.2)
        self.assertEqual(config.uninformed_trader_lambda, 0.8)
        self.assertEqual(config.market_maker_count, 5)
        self.assertEqual(config.initial_capital, 200000.0)
        self.assertEqual(config.max_position, 2000)


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager()
    
    def test_default_configuration(self):
        """Test default configuration manager setup."""
        self.assertIsInstance(self.config.simulation, SimulationConfig)
        self.assertIsInstance(self.config.agent, AgentConfig)
        self.assertIsInstance(self.config.orderbook, OrderBookConfig)
        self.assertIsInstance(self.config.strategy, StrategyConfig)
        self.assertIsInstance(self.config.web, WebConfig)
        self.assertIsInstance(self.config.logging, LoggingConfig)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            # Modify some values
            self.config.simulation.initial_price = 150.0
            self.config.agent.market_maker_count = 5
            
            # Save configuration
            self.config.save_to_file(config_file)
            
            # Create new config manager and load
            new_config = ConfigManager(config_file)
            
            # Check that values were loaded correctly
            self.assertEqual(new_config.simulation.initial_price, 150.0)
            self.assertEqual(new_config.agent.market_maker_count, 5)
            
        finally:
            # Clean up
            if os.path.exists(config_file):
                os.unlink(config_file)
    
    def test_get_all_config(self):
        """Test getting all configuration as dictionary."""
        config_dict = self.config.get_all_config()
        
        self.assertIn('simulation', config_dict)
        self.assertIn('agent', config_dict)
        self.assertIn('orderbook', config_dict)
        self.assertIn('strategy', config_dict)
        self.assertIn('web', config_dict)
        self.assertIn('logging', config_dict)
        
        # Check that values are correctly serialized
        self.assertEqual(config_dict['simulation']['initial_price'], 100.0)
        self.assertEqual(config_dict['agent']['market_maker_count'], 3)
    
    def test_update_config(self):
        """Test updating configuration."""
        # Update simulation config
        self.config.update_config('simulation', initial_price=200.0, tick_size=0.02)
        
        self.assertEqual(self.config.simulation.initial_price, 200.0)
        self.assertEqual(self.config.simulation.tick_size, 0.02)
        
        # Update agent config
        self.config.update_config('agent', market_maker_count=7, initial_capital=300000.0)
        
        self.assertEqual(self.config.agent.market_maker_count, 7)
        self.assertEqual(self.config.agent.initial_capital, 300000.0)
    
    def test_load_nonexistent_file(self):
        """Test loading configuration from nonexistent file."""
        config = ConfigManager('nonexistent_file.json')
        
        # Should not raise an error and should use default values
        self.assertEqual(config.simulation.initial_price, 100.0)
        self.assertEqual(config.agent.market_maker_count, 3)


class TestEnvironmentVariableLoading(unittest.TestCase):
    """Test loading configuration from environment variables."""
    
    @patch.dict(os.environ, {
        'LOB_INITIAL_PRICE': '150.0',
        'LOB_SIMULATION_DURATION': '1800.0',
        'LOB_HOST': '0.0.0.0',
        'LOB_PORT': '9090',
        'LOB_DEBUG': 'false',
        'LOB_LOG_LEVEL': 'DEBUG',
        'LOB_LOG_FILE': '/tmp/test.log'
    })
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        from config.settings import load_config_from_env, config
        
        load_config_from_env()
        
        self.assertEqual(config.simulation.initial_price, 150.0)
        self.assertEqual(config.simulation.simulation_duration, 1800.0)
        self.assertEqual(config.web.host, '0.0.0.0')
        self.assertEqual(config.web.port, 9090)
        self.assertFalse(config.web.debug)
        self.assertEqual(config.logging.level, 'DEBUG')
        self.assertEqual(config.logging.file, '/tmp/test.log')


if __name__ == '__main__':
    unittest.main() 