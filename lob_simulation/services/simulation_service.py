"""
Simulation Service

This service encapsulates the business logic for managing simulations,
providing a clean interface for different frontends (web, CLI, API).
"""

from typing import Dict, Any, Optional, List
from ..core.interfaces import SimulationEngine, SimulationConfig
from ..core.simulation import LimitOrderBookSimulation
from ..strategies import create_strategy


class SimulationService:
    """Service for managing simulation lifecycle and operations."""
    
    def __init__(self):
        self.simulation: Optional[LimitOrderBookSimulation] = None
        self.is_running = False
    
    def start_simulation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new simulation with the given configuration."""
        try:
            # Create simulation config
            sim_config = SimulationConfig(
                duration=config.get('duration', 3600.0),
                tick_size=config.get('tick_size', 0.01),
                max_levels=config.get('max_levels', 10),
                initial_price=config.get('initial_price', 100.0),
                num_informed_traders=config.get('num_informed_traders', 5),
                num_uninformed_traders=config.get('num_uninformed_traders', 20),
                num_market_makers=config.get('num_market_makers', 3),
                strategies=config.get('strategies', {}),
                refresh_rate=config.get('refresh_rate', 1.0)
            )
            
            # Create simulation
            self.simulation = LimitOrderBookSimulation(sim_config)
            
            # Add strategies
            for strategy_name, strategy_config in sim_config.strategies.items():
                self.simulation.add_strategy(strategy_name, strategy_config)
            
            # Initialize simulation
            self.simulation._schedule_initial_events()
            self.simulation.run_step(max_events=50)
            
            self.is_running = True
            
            return {
                "status": "started",
                "config": config,
                "initial_events": len(self.simulation.event_queue)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stop_simulation(self) -> Dict[str, Any]:
        """Stop the current simulation."""
        try:
            self.is_running = False
            if self.simulation:
                self.simulation.stop()
            
            return {"status": "stopped"}
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        if not self.simulation:
            return {
                "running": False,
                "time": 0.0,
                "events_in_queue": 0
            }
        
        return {
            "running": self.is_running,
            "time": self.simulation.current_time,
            "events_in_queue": len(self.simulation.event_queue)
        }
    
    def step_simulation(self, max_events: int = 10) -> Dict[str, Any]:
        """Run simulation for one step."""
        if not self.simulation or not self.is_running:
            return {"status": "not_running"}
        
        try:
            self.simulation.run_step(max_events)
            return {
                "status": "success",
                "time": self.simulation.current_time,
                "events_processed": max_events
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data."""
        if not self.simulation:
            return {"error": "No simulation running"}
        
        try:
            # Get order book state
            order_book_state = self.simulation.order_book.get_state()
            
            # Convert depth format
            bids = [{'price': price, 'quantity': volume} 
                   for price, volume in order_book_state.get('depth', {}).get('bids', [])]
            asks = [{'price': price, 'quantity': volume} 
                   for price, volume in order_book_state.get('depth', {}).get('asks', [])]
            
            order_book_data = {
                'bids': bids,
                'asks': asks,
                'best_bid': order_book_state.get('best_bid', 0.0),
                'best_ask': order_book_state.get('best_ask', 0.0),
                'mid_price': order_book_state.get('mid_price', 0.0),
                'spread': order_book_state.get('spread', 0.0)
            }
            
            # Get price history
            price_data = self.simulation.price_history[-100:] if self.simulation.price_history else []
            prices = [entry.get('mid_price', 100.0) for entry in price_data]
            times = [entry.get('timestamp', 0.0) for entry in price_data]
            
            # Get trade history
            trade_history = []
            for trade in self.simulation.trades[-50:]:
                if hasattr(trade, 'process'):
                    trade_history.append(trade.process())
                else:
                    trade_history.append({
                        'trade_id': getattr(trade, 'trade_id', 'unknown'),
                        'price': getattr(trade, 'price', 0.0),
                        'quantity': getattr(trade, 'quantity', 0),
                        'timestamp': getattr(trade, 'timestamp', 0.0)
                    })
            
            # Get strategy performance
            strategy_performance = {}
            for strategy_name in self.simulation.strategies:
                strategy_performance[strategy_name] = self.simulation.get_strategy_performance(strategy_name)
            
            return {
                'order_book': order_book_data,
                'price_history': {
                    'prices': prices,
                    'times': times
                },
                'trade_history': trade_history,
                'simulation_time': self.simulation.current_time,
                'strategy_performance': strategy_performance
            }
            
        except Exception as e:
            return {"error": str(e)} 