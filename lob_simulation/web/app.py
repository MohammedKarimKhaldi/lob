"""
Web application module for the LOB simulation.
Modular Flask application with WebSocket support.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from typing import Dict, Any, Optional

from config.settings import get_config
from lob_simulation.utils.logger import get_logger, LoggerMixin
from lob_simulation.core.simulation import LimitOrderBookSimulation


class WebApplication(LoggerMixin):
    """Modular web application for the LOB simulation."""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.simulation: Optional[LimitOrderBookSimulation] = None
        self.simulation_thread: Optional[threading.Thread] = None
        self.is_running = False
        
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
                
                # Get strategy configuration from request
                strategy_config = request.json.get('strategies', {})
                
                # Initialize simulation
                self.simulation = LimitOrderBookSimulation()
                
                # Add strategies
                for strategy_name, config in strategy_config.items():
                    self.simulation.add_strategy(strategy_name, config)
                
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
                
                order_book_data = self.simulation.order_book.get_order_book_data()
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
                
                return jsonify({
                    "prices": self.simulation.price_history,
                    "times": self.simulation.price_times
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
                
                return jsonify({
                    "trades": self.simulation.trade_history
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
                
                performance = {}
                for strategy_name in self.simulation.strategies:
                    performance[strategy_name] = self.simulation.get_strategy_performance(strategy_name)
                
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
                # Send current market state
                market_data = {
                    'order_book': self.simulation.order_book.get_order_book_data(),
                    'price_history': {
                        'prices': self.simulation.price_history[-100:],  # Last 100 prices
                        'times': self.simulation.price_times[-100:]
                    },
                    'trade_history': self.simulation.trade_history[-50:],  # Last 50 trades
                    'simulation_time': self.simulation.current_time
                }
                emit('market_update', market_data)
    
    def _run_simulation_loop(self) -> None:
        """Run the simulation loop in background thread."""
        try:
            while self.is_running and self.simulation:
                # Run simulation for a short time
                self.simulation.run_step()
                
                # Send updates via WebSocket
                if self.simulation.current_time % 1.0 < 0.1:  # Every ~1 second
                    self._broadcast_market_update()
                
                time.sleep(0.01)  # Small delay to prevent overwhelming
                
        except Exception as e:
            self.log_exception(f"Error in simulation loop: {e}")
            self.is_running = False
    
    def _broadcast_market_update(self) -> None:
        """Broadcast market update to all connected clients."""
        try:
            if not self.simulation:
                return
            
            market_data = {
                'order_book': self.simulation.order_book.get_order_book_data(),
                'price_history': {
                    'prices': self.simulation.price_history[-100:],
                    'times': self.simulation.price_times[-100:]
                },
                'trade_history': self.simulation.trade_history[-50:],
                'simulation_time': self.simulation.current_time,
                'strategy_performance': {}
            }
            
            # Add strategy performance
            for strategy_name in self.simulation.strategies:
                market_data['strategy_performance'][strategy_name] = \
                    self.simulation.get_strategy_performance(strategy_name)
            
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