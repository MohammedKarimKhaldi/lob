"""
Unit tests for the Limit Order Book Simulation

This module contains comprehensive tests for all simulation components.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from lob_simulation.simulation import LimitOrderBookSimulation, SimulationConfig
from lob_simulation.orderbook import OrderBook
from lob_simulation.events import OrderEvent, CancelEvent, TradeEvent
from lob_simulation.agents import InformedTrader, UninformedTrader, MarketMaker


class TestSimulationConfig(unittest.TestCase):
    """Test simulation configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()
        
        self.assertEqual(config.duration, 3600.0)
        self.assertEqual(config.initial_price, 100.0)
        self.assertEqual(config.tick_size, 0.01)
        self.assertEqual(config.max_levels, 10)
        self.assertEqual(config.num_informed_traders, 5)
        self.assertEqual(config.num_uninformed_traders, 20)
        self.assertEqual(config.num_market_makers, 3)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = SimulationConfig(
            duration=1800.0,
            initial_price=50.0,
            tick_size=0.05,
            max_levels=5,
            num_informed_traders=2,
            num_uninformed_traders=10,
            num_market_makers=1
        )
        
        self.assertEqual(config.duration, 1800.0)
        self.assertEqual(config.initial_price, 50.0)
        self.assertEqual(config.tick_size, 0.05)
        self.assertEqual(config.max_levels, 5)
        self.assertEqual(config.num_informed_traders, 2)
        self.assertEqual(config.num_uninformed_traders, 10)
        self.assertEqual(config.num_market_makers, 1)


class TestOrderBook(unittest.TestCase):
    """Test order book functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orderbook = OrderBook(tick_size=0.01, max_levels=5)
    
    def test_add_buy_order(self):
        """Test adding a buy order."""
        order_event = OrderEvent(
            order_id="test_buy_1",
            trader_id="trader_1",
            side="buy",
            price=100.0,
            quantity=100,
            timestamp=0.0
        )
        
        trades = self.orderbook.add_order(order_event)
        
        self.assertEqual(len(trades), 0)  # No immediate trades
        self.assertEqual(self.orderbook.best_bid, 100.0)
        self.assertEqual(self.orderbook.get_bid_volume(), 100)
    
    def test_add_sell_order(self):
        """Test adding a sell order."""
        order_event = OrderEvent(
            order_id="test_sell_1",
            trader_id="trader_2",
            side="sell",
            price=101.0,
            quantity=50,
            timestamp=0.0
        )
        
        trades = self.orderbook.add_order(order_event)
        
        self.assertEqual(len(trades), 0)  # No immediate trades
        self.assertEqual(self.orderbook.best_ask, 101.0)
        self.assertEqual(self.orderbook.get_ask_volume(), 50)
    
    def test_matching_orders(self):
        """Test order matching."""
        # Add buy order
        buy_order = OrderEvent(
            order_id="buy_1",
            trader_id="trader_1",
            side="buy",
            price=100.0,
            quantity=100,
            timestamp=0.0
        )
        self.orderbook.add_order(buy_order)
        
        # Add sell order that matches
        sell_order = OrderEvent(
            order_id="sell_1",
            trader_id="trader_2",
            side="sell",
            price=100.0,
            quantity=50,
            timestamp=1.0
        )
        trades = self.orderbook.add_order(sell_order)
        
        self.assertEqual(len(trades), 1)  # One trade should occur
        self.assertEqual(trades[0].price, 100.0)
        self.assertEqual(trades[0].quantity, 50)
    
    def test_cancel_order(self):
        """Test order cancellation."""
        order_event = OrderEvent(
            order_id="test_cancel_1",
            trader_id="trader_1",
            side="buy",
            price=100.0,
            quantity=100,
            timestamp=0.0
        )
        
        self.orderbook.add_order(order_event)
        self.assertEqual(self.orderbook.get_bid_volume(), 100)
        
        cancel_event = CancelEvent("test_cancel_1", "trader_1", 1.0)
        success = self.orderbook.cancel_order("test_cancel_1")
        
        self.assertTrue(success)
        self.assertEqual(self.orderbook.get_bid_volume(), 0)


class TestEvents(unittest.TestCase):
    """Test event system."""
    
    def test_order_event(self):
        """Test order event creation and processing."""
        order_event = OrderEvent(
            order_id="test_order",
            trader_id="test_trader",
            side="buy",
            price=100.0,
            quantity=100,
            timestamp=0.0,
            order_type="limit"
        )
        
        self.assertEqual(order_event.order_id, "test_order")
        self.assertEqual(order_event.trader_id, "test_trader")
        self.assertEqual(order_event.side, "buy")
        self.assertEqual(order_event.price, 100.0)
        self.assertEqual(order_event.quantity, 100)
        self.assertEqual(order_event.timestamp, 0.0)
        self.assertEqual(order_event.order_type, "limit")
        
        # Test processing
        result = order_event.process()
        self.assertEqual(result['order_id'], "test_order")
        self.assertEqual(result['side'], "buy")
    
    def test_trade_event(self):
        """Test trade event creation and processing."""
        trade_event = TradeEvent(
            trade_id="test_trade",
            buy_order_id="buy_1",
            sell_order_id="sell_1",
            price=100.0,
            quantity=50,
            timestamp=1.0
        )
        
        self.assertEqual(trade_event.trade_id, "test_trade")
        self.assertEqual(trade_event.buy_order_id, "buy_1")
        self.assertEqual(trade_event.sell_order_id, "sell_1")
        self.assertEqual(trade_event.price, 100.0)
        self.assertEqual(trade_event.quantity, 50)
        self.assertEqual(trade_event.timestamp, 1.0)
        
        # Test processing
        result = trade_event.process()
        self.assertEqual(result['trade_id'], "test_trade")
        self.assertEqual(result['price'], 100.0)


class TestAgents(unittest.TestCase):
    """Test agent behavior."""
    
    def test_informed_trader(self):
        """Test informed trader creation and behavior."""
        trader = InformedTrader(
            trader_id="informed_1",
            arrival_rate=0.1,
            private_info_prob=0.1
        )
        
        self.assertEqual(trader.trader_id, "informed_1")
        self.assertEqual(trader.arrival_rate, 0.1)
        self.assertEqual(trader.private_info_prob, 0.1)
        self.assertFalse(trader.has_private_info)
    
    def test_uninformed_trader(self):
        """Test uninformed trader creation."""
        trader = UninformedTrader(
            trader_id="uninformed_1",
            arrival_rate=0.5
        )
        
        self.assertEqual(trader.trader_id, "uninformed_1")
        self.assertEqual(trader.arrival_rate, 0.5)
    
    def test_market_maker(self):
        """Test market maker creation and behavior."""
        mm = MarketMaker(
            trader_id="mm_1",
            arrival_rate=0.2,
            inventory_target=0.0,
            max_inventory=1000
        )
        
        self.assertEqual(mm.trader_id, "mm_1")
        self.assertEqual(mm.arrival_rate, 0.2)
        self.assertEqual(mm.inventory_target, 0.0)
        self.assertEqual(mm.max_inventory, 1000)
        self.assertEqual(mm.inventory, 0)
    
    def test_agent_pnl_update(self):
        """Test P&L update functionality."""
        trader = InformedTrader("test_trader", 0.1)
        
        # Initial state
        self.assertEqual(trader.cash, 100000.0)
        self.assertEqual(trader.inventory, 0)
        self.assertEqual(trader.pnl, 0.0)
        
        # Update P&L for a buy trade
        trader.update_pnl(100.0, 50, "buy")
        
        self.assertEqual(trader.inventory, 50)
        self.assertEqual(trader.cash, 100000.0 - 100.0 * 50)
        
        # Update P&L for a sell trade
        trader.update_pnl(101.0, 25, "sell")
        
        self.assertEqual(trader.inventory, 25)
        self.assertEqual(trader.cash, 100000.0 - 100.0 * 50 + 101.0 * 25)


class TestSimulation(unittest.TestCase):
    """Test main simulation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(
            duration=60.0,  # Short duration for testing
            initial_price=100.0,
            tick_size=0.01,
            max_levels=5,
            num_informed_traders=1,
            num_uninformed_traders=2,
            num_market_makers=1
        )
        self.simulation = LimitOrderBookSimulation(self.config)
    
    def test_simulation_initialization(self):
        """Test simulation initialization."""
        self.assertEqual(self.simulation.config.duration, 60.0)
        self.assertEqual(self.simulation.config.initial_price, 100.0)
        self.assertEqual(self.simulation.mid_price, 100.0)
        self.assertEqual(len(self.simulation.agents['informed']), 1)
        self.assertEqual(len(self.simulation.agents['uninformed']), 2)
        self.assertEqual(len(self.simulation.agents['market_makers']), 1)
    
    def test_simulation_reset(self):
        """Test simulation reset functionality."""
        # Add some data
        self.simulation.current_time = 10.0
        self.simulation.trades.append(TradeEvent("test", "buy", "sell", 100.0, 10, 5.0))
        
        # Reset
        self.simulation.reset()
        
        self.assertEqual(self.simulation.current_time, 0.0)
        self.assertEqual(len(self.simulation.trades), 0)
        self.assertEqual(len(self.simulation.order_events), 0)
        self.assertEqual(self.simulation.mid_price, 100.0)
    
    def test_orderbook_snapshot(self):
        """Test order book snapshot functionality."""
        snapshot = self.simulation.get_orderbook_snapshot()
        
        self.assertIn('best_bid', snapshot)
        self.assertIn('best_ask', snapshot)
        self.assertIn('mid_price', snapshot)
        self.assertIn('spread', snapshot)
        self.assertIn('depth', snapshot)
    
    def test_custom_event_addition(self):
        """Test adding custom events to simulation."""
        order_event = OrderEvent(
            order_id="custom_order",
            trader_id="custom_trader",
            side="buy",
            price=100.0,
            quantity=100,
            timestamp=1.0
        )
        
        self.simulation.add_custom_event(order_event)
        
        # Check that event was added to queue
        self.assertEqual(len(self.simulation.event_queue), 1)
        event_time, event = self.simulation.event_queue[0]
        self.assertEqual(event_time, 1.0)
        self.assertEqual(event.order_id, "custom_order")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_simple_simulation_run(self):
        """Test a simple simulation run."""
        config = SimulationConfig(
            duration=10.0,  # Very short for testing
            initial_price=100.0,
            tick_size=0.01,
            max_levels=3,
            num_informed_traders=1,
            num_uninformed_traders=1,
            num_market_makers=1
        )
        
        simulation = LimitOrderBookSimulation(config)
        results = simulation.run()
        
        # Check that results contain expected keys
        self.assertIn('config', results)
        self.assertIn('trades', results)
        self.assertIn('order_events', results)
        self.assertIn('price_history', results)
        self.assertIn('spread_history', results)
        self.assertIn('volume_history', results)
        self.assertIn('orderbook_state', results)
        
        # Check that simulation completed
        self.assertGreaterEqual(simulation.current_time, 10.0)
    
    def test_simulation_with_custom_events(self):
        """Test simulation with custom events."""
        config = SimulationConfig(duration=5.0)
        simulation = LimitOrderBookSimulation(config)
        
        # Add some custom orders
        for i in range(5):
            order_event = OrderEvent(
                order_id=f"custom_{i}",
                trader_id="test_trader",
                side="buy" if i % 2 == 0 else "sell",
                price=100.0 + (i * 0.01),
                quantity=10,
                timestamp=i * 0.5
            )
            simulation.add_custom_event(order_event)
        
        results = simulation.run()
        
        # Should have processed the custom events
        self.assertGreater(len(results['order_events']), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 