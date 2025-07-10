"""
Web application module for the LOB simulation.
Modular Flask application with WebSocket support.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import get_config
from lob_simulation.utils.logger import get_logger, LoggerMixin
from lob_simulation.core.simulation import LimitOrderBookSimulation


class WebApplication(LoggerMixin):
    """Modular web application for the LOB simulation."""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.app = Flask(__name__, template_folder='../../templates', static_folder='../../static')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.simulation: Optional[LimitOrderBookSimulation] = None
        self.simulation_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.refresh_rate = 1.0
        
        self._setup_routes()
        self._setup_socketio_events()
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main page."""
            return render_template('index.html')
        
        @self.app.route('/api/start_simulation', methods=['POST'])
        def start_simulation():
            """Start the simulation."""
            try:
                if self.is_running:
                    return jsonify({"error": "Simulation already running"}), 400
                
                # Get strategy configuration and refresh rate from request
                strategy_config = request.json.get('strategies', {}) if request.json else {}
                refresh_rate = request.json.get('refresh_rate', 1.0) if request.json else 1.0
                
                # Debug: Log strategy configuration
                self.log_info(f"Starting simulation with strategies: {list(strategy_config.keys())}")
                self.log_info(f"Strategy config details: {strategy_config}")
                
                # Store refresh rate for the simulation loop
                self.refresh_rate = refresh_rate
                
                # Initialize simulation
                self.simulation = LimitOrderBookSimulation()
                
                # Add strategies
                from lob_simulation.strategies import StrategyConfig
                for strategy_name, config_dict in strategy_config.items():
                    config = StrategyConfig(
                        strategy_name=strategy_name,
                        initial_capital=config_dict.get('initial_capital', 10000),
                        max_position=config_dict.get('max_position', 100),
                        min_spread=config_dict.get('min_spread', 0.01),
                        max_spread=config_dict.get('max_spread', 0.05)
                    )
                    self.simulation.add_strategy(strategy_name, config)
                    self.log_info(f"Added strategy: {strategy_name}")

                # PATCH: Explicitly update all strategies with current market state and trigger initial orders
                market_data = {
                    'mid_price': self.simulation.mid_price,
                    'best_bid': self.simulation.best_bid,
                    'best_ask': self.simulation.best_ask,
                    'spread': self.simulation.best_ask - self.simulation.best_bid,
                    'bid_volume': self.simulation.orderbook.get_bid_volume(),
                    'ask_volume': self.simulation.orderbook.get_ask_volume(),
                    'timestamp': self.simulation.current_time
                }
                for strategy in self.simulation.strategies.values():
                    strategy.update_market_data(market_data)
                    strategy.generate_orders(self.simulation.current_time, market_data)
                
                # Debug: Log all strategies in simulation
                self.log_info(f"All strategies in simulation: {list(self.simulation.strategies.keys())}")
                
                # Schedule initial events
                self.simulation._schedule_initial_events()
                self.log_info(f"Initial events scheduled: {len(self.simulation.event_queue)} events")
                
                # Force some immediate events to populate the order book
                self.simulation.run_step(max_events=50)
                self.log_info(f"After initial step: {len(self.simulation.order_book.bids)} bid levels, {len(self.simulation.order_book.asks)} ask levels")
                
                # Start simulation in background thread
                self.is_running = True
                self.simulation_thread = threading.Thread(
                    target=self._run_simulation_loop,
                    daemon=True
                )
                self.simulation_thread.start()
                
                self.log_info("Simulation started")
                return jsonify({"status": "started"})
            
            except Exception as e:
                self.log_exception(f"Error starting simulation: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/stop_simulation', methods=['POST'])
        def stop_simulation():
            """Stop the simulation."""
            try:
                self.is_running = False
                if self.simulation:
                    self.simulation.stop()
                self.log_info("Simulation stopped")
                return jsonify({"status": "stopped"})
            except Exception as e:
                self.log_exception(f"Error stopping simulation: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/simulation_status')
        def simulation_status():
            """Get simulation status."""
            try:
                if not self.simulation:
                    return jsonify({
                        "running": False,
                        "time": 0.0,
                        "events_in_queue": 0
                    })
                
                return jsonify({
                    "running": self.is_running,
                    "time": self.simulation.current_time,
                    "events_in_queue": len(self.simulation.event_queue)
                })
            except Exception as e:
                self.log_exception(f"Error getting simulation status: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/order_book')
        def order_book():
            """Get current order book state."""
            try:
                if not self.simulation:
                    return jsonify({"error": "No simulation running"}), 400
                
                order_book_data = self.simulation.order_book.get_state()
                return jsonify(order_book_data)
            except Exception as e:
                self.log_exception(f"Error getting order book: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/price_history')
        def price_history():
            """Get price history."""
            try:
                if not self.simulation:
                    return jsonify({"error": "No simulation running"}), 400
                
                # Extract price data from price_history
                price_data = self.simulation.price_history
                prices = [entry.get('mid_price', 100.0) for entry in price_data]
                times = [entry.get('timestamp', 0.0) for entry in price_data]
                
                return jsonify({
                    "prices": prices,
                    "times": times
                })
            except Exception as e:
                self.log_exception(f"Error getting price history: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/trade_history')
        def trade_history():
            """Get trade history."""
            try:
                if not self.simulation:
                    return jsonify({"error": "No simulation running"}), 400
                
                # Convert trade events to dictionaries for JSON serialization
                trades = []
                for trade in self.simulation.trades:
                    if hasattr(trade, 'process'):
                        trades.append(trade.process())
                    else:
                        # Fallback for non-event objects
                        trades.append({
                            'trade_id': getattr(trade, 'trade_id', 'unknown'),
                            'price': getattr(trade, 'price', 0.0),
                            'quantity': getattr(trade, 'quantity', 0),
                            'timestamp': getattr(trade, 'timestamp', 0.0)
                        })
                
                return jsonify({
                    "trades": trades
                })
            except Exception as e:
                self.log_exception(f"Error getting trade history: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/strategy_performance')
        def strategy_performance():
            """Get strategy performance."""
            try:
                if not self.simulation:
                    return jsonify({"error": "No simulation running"}), 400
                
                # Debug: Log available strategies
                self.log_info(f"Available strategies: {list(self.simulation.strategies.keys())}")
                
                performance = {}
                for strategy_name in self.simulation.strategies:
                    strategy_perf = self.simulation.get_strategy_performance(strategy_name)
                    performance[strategy_name] = strategy_perf
                    self.log_info(f"Strategy {strategy_name} performance: {strategy_perf}")
                
                # Debug: Log final performance object
                self.log_info(f"Returning performance for {len(performance)} strategies: {list(performance.keys())}")
                
                return jsonify(performance)
            except Exception as e:
                self.log_exception(f"Error getting strategy performance: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_socketio_events(self) -> None:
        """Setup SocketIO events."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.log_info("Client connected")
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.log_info("Client disconnected")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle update request from client."""
            if self.simulation and self.is_running:
                # Convert trade events to dictionaries for JSON serialization
                trade_history = []
                for trade in self.simulation.trades[-50:]:
                    if hasattr(trade, 'process'):
                        trade_history.append(trade.process())
                    else:
                        # Fallback for non-event objects
                        trade_history.append({
                            'trade_id': getattr(trade, 'trade_id', 'unknown'),
                            'price': getattr(trade, 'price', 0.0),
                            'quantity': getattr(trade, 'quantity', 0),
                            'timestamp': getattr(trade, 'timestamp', 0.0)
                        })
                
                # Extract price data from price_history
                price_data = self.simulation.price_history[-100:] if self.simulation.price_history else []
                prices = [entry.get('mid_price', 100.0) for entry in price_data]
                times = [entry.get('timestamp', 0.0) for entry in price_data]
                
                # Get order book state and convert to frontend format
                order_book_state = self.simulation.order_book.get_state()
                
                # Convert depth format from (price, volume) tuples to {price, quantity} objects
                bids = [{'price': price, 'quantity': volume} for price, volume in order_book_state.get('depth', {}).get('bids', [])]
                asks = [{'price': price, 'quantity': volume} for price, volume in order_book_state.get('depth', {}).get('asks', [])]
                
                # Create order book data in frontend format
                order_book_data = {
                    'bids': bids,
                    'asks': asks,
                    'best_bid': order_book_state.get('best_bid', 0.0),
                    'best_ask': order_book_state.get('best_ask', 0.0),
                    'mid_price': order_book_state.get('mid_price', 0.0),
                    'spread': order_book_state.get('spread', 0.0)
                }
                
                # Get strategy performance
                strategy_performance = {}
                for strategy_name in self.simulation.strategies:
                    strategy_performance[strategy_name] = \
                        self.simulation.get_strategy_performance(strategy_name)
                
                # Debug: Log strategy performance being sent
                self.log_info(f"WebSocket sending performance for {len(strategy_performance)} strategies: {list(strategy_performance.keys())}")
                
                # Send current market state
                market_data = {
                    'order_book': order_book_data,
                    'price_history': {
                        'prices': prices,  # Last 100 prices
                        'times': times
                    },
                    'trade_history': trade_history,  # Last 50 trades
                    'simulation_time': self.simulation.current_time,
                    'strategy_performance': strategy_performance
                }
                emit('market_update', market_data)
    
    def _run_simulation_loop(self) -> None:
        """Run the simulation loop in background thread."""
        try:
            self.log_info("Simulation loop started")
            
            while self.is_running and self.simulation:
                # Run simulation for a short time - process more events
                self.simulation.run_step(max_events=20)
                
                # Don't automatically broadcast updates - let frontend request them
                time.sleep(0.005)  # Smaller delay for more frequent updates
                
        except Exception as e:
            self.log_exception(f"Error in simulation loop: {e}")
            self.is_running = False
    
    def _broadcast_market_update(self) -> None:
        """Broadcast market update to all connected clients."""
        try:
            if not self.simulation:
                self.log_info("No simulation running, skipping broadcast")
                return
            
            # Convert trade events to dictionaries for JSON serialization
            trade_history = []
            for trade in self.simulation.trades[-50:]:
                if hasattr(trade, 'process'):
                    trade_history.append(trade.process())
                else:
                    # Fallback for non-event objects
                    trade_history.append({
                        'trade_id': getattr(trade, 'trade_id', 'unknown'),
                        'price': getattr(trade, 'price', 0.0),
                        'quantity': getattr(trade, 'quantity', 0),
                        'timestamp': getattr(trade, 'timestamp', 0.0)
                    })
            
            # Extract price data from price_history
            price_data = self.simulation.price_history[-100:] if self.simulation.price_history else []
            prices = [entry.get('mid_price', 100.0) for entry in price_data]
            times = [entry.get('timestamp', 0.0) for entry in price_data]
            
            # Add some debugging
            self.log_info(f"Price history: {len(self.simulation.price_history)} entries, sending {len(prices)} prices")
            if prices:
                self.log_info(f"Price range: {min(prices):.2f} - {max(prices):.2f}")
            else:
                self.log_info("No price data available")
            
            # Get order book state and convert to frontend format
            order_book_state = self.simulation.order_book.get_state()
            
            # Convert depth format from (price, volume) tuples to {price, quantity} objects
            bids = [{'price': price, 'quantity': volume} for price, volume in order_book_state.get('depth', {}).get('bids', [])]
            asks = [{'price': price, 'quantity': volume} for price, volume in order_book_state.get('depth', {}).get('asks', [])]
            
            # Create order book data in frontend format
            order_book_data = {
                'bids': bids,
                'asks': asks,
                'best_bid': order_book_state.get('best_bid', 0.0),
                'best_ask': order_book_state.get('best_ask', 0.0),
                'mid_price': order_book_state.get('mid_price', 0.0),
                'spread': order_book_state.get('spread', 0.0)
            }
            
            # Add debugging for order book
            self.log_info(f"Order book: {len(bids)} bids, {len(asks)} asks")
            if bids:
                self.log_info(f"Best bid: {bids[0]['price']:.2f} @ {bids[0]['quantity']}")
            if asks:
                self.log_info(f"Best ask: {asks[0]['price']:.2f} @ {asks[0]['quantity']}")
            
            market_data = {
                'order_book': order_book_data,
                'price_history': {
                    'prices': prices,
                    'times': times
                },
                'trade_history': trade_history,
                'simulation_time': self.simulation.current_time,
                'strategy_performance': {}
            }
            
            # Add strategy performance
            for strategy_name in self.simulation.strategies:
                market_data['strategy_performance'][strategy_name] = \
                    self.simulation.get_strategy_performance(strategy_name)
            
            self.log_info(f"Broadcasting market update: {len(prices)} prices, {len(trade_history)} trades")
            self.socketio.emit('market_update', market_data)
            
        except Exception as e:
            self.log_exception(f"Error broadcasting market update: {e}")
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, 
            debug: Optional[bool] = None) -> None:
        """Run the web application."""
        host = host or self.config.web.host
        port = port or self.config.web.port
        debug = debug if debug is not None else self.config.web.debug
        
        self.log_info(f"Starting LOB Simulation Web Application...")
        self.log_info(f"Open http://{host}:{port} in your browser")
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )


def create_app() -> WebApplication:
    """Create and return a web application instance."""
    return WebApplication()


def run_web_app(host: Optional[str] = None, port: Optional[int] = None, 
                debug: Optional[bool] = None) -> None:
    """Run the web application."""
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web_app() 