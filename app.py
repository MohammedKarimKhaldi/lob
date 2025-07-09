"""
Web Application for Limit Order Book Simulation

Real-time visualization using WebSocket protocols and D3.js
for interactive limit order book simulation and analysis.
"""

import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import numpy as np
import pandas as pd
import heapq

from lob_simulation import LimitOrderBookSimulation, SimulationConfig
from lob_simulation.strategies import StrategyConfig


app = Flask(__name__)
app.config['SECRET_KEY'] = 'lob-simulation-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global simulation state
simulation = None
simulation_thread = None
is_running = False


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start a new simulation."""
    global simulation, simulation_thread, is_running
    
    if is_running:
        return jsonify({'error': 'Simulation already running'}), 400
    
    try:
        data = request.get_json()
        
        # Create simulation configuration
        config = SimulationConfig(
            duration=data.get('duration', 3600.0),
            initial_price=data.get('initial_price', 100.0),
            tick_size=data.get('tick_size', 0.01),
            max_levels=data.get('max_levels', 10),
            num_informed_traders=data.get('num_informed_traders', 5),
            num_uninformed_traders=data.get('num_uninformed_traders', 20),
            num_market_makers=data.get('num_market_makers', 3),
            lambda_informed=data.get('lambda_informed', 0.1),
            lambda_uninformed=data.get('lambda_uninformed', 0.5),
            lambda_market_maker=data.get('lambda_market_maker', 0.2)
        )
        
        # Initialize simulation
        simulation = LimitOrderBookSimulation(config)
        
        # Add strategies
        strategies_config = data.get('strategies', [])
        for strategy_config in strategies_config:
            strategy_name = strategy_config.get('name', 'market_making')
            strategy_params = strategy_config.get('params', {})
            
            config = StrategyConfig(
                strategy_name=strategy_name,
                initial_capital=strategy_params.get('initial_capital', 100000.0),
                max_position=strategy_params.get('max_position', 1000),
                max_order_size=strategy_params.get('max_order_size', 100),
                min_spread=strategy_params.get('min_spread', 0.01),
                max_spread=strategy_params.get('max_spread', 0.10),
                lookback_period=strategy_params.get('lookback_period', 20),
                momentum_threshold=strategy_params.get('momentum_threshold', 0.02),
                mean_reversion_threshold=strategy_params.get('mean_reversion_threshold', 0.03),
                arbitrage_threshold=strategy_params.get('arbitrage_threshold', 0.005)
            )
            
            simulation.add_strategy(strategy_name, config)
        
        is_running = True
        
        # Start simulation in background thread
        simulation_thread = threading.Thread(target=run_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()
        
        return jsonify({'status': 'started', 'config': data, 'strategies': strategies_config})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stop_simulation', methods=['POST'])
def stop_simulation():
    """Stop the current simulation."""
    global is_running
    
    is_running = False
    return jsonify({'status': 'stopped'})


@app.route('/api/simulation_status')
def simulation_status():
    """Get current simulation status."""
    global simulation, is_running
    
    if simulation is None:
        return jsonify({'status': 'not_started'})
    
    orderbook_state = simulation.get_orderbook_snapshot()
    
    return jsonify({
        'status': 'running' if is_running else 'stopped',
        'current_time': simulation.current_time,
        'orderbook': orderbook_state,
        'num_trades': len(simulation.trades),
        'num_orders': len(simulation.order_events)
    })


@app.route('/api/results')
def get_results():
    """Get simulation results."""
    global simulation
    
    if simulation is None:
        return jsonify({'error': 'No simulation available'}), 404
    
    results = simulation.get_results()
    
    # Convert to JSON-serializable format
    def convert_to_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return obj
    
    # Convert results
    json_results = {}
    for key, value in results.items():
        if key == 'config':
            json_results[key] = value.__dict__
        else:
            json_results[key] = convert_to_json(value)
    
    # Add strategy performance
    json_results['strategy_performance'] = simulation.get_all_strategy_performance()
    
    return jsonify(json_results)


@app.route('/api/strategy_performance')
def get_strategy_performance():
    """Get strategy performance data."""
    global simulation
    
    if simulation is None:
        return jsonify({'error': 'No simulation available'}), 404
    
    return jsonify(simulation.get_all_strategy_performance())


def run_simulation():
    """Run simulation in background thread."""
    global simulation, is_running
    
    try:
        # Initialize event queue with agent events
        simulation._schedule_initial_events()
        print(f"Initialized simulation with {len(simulation.event_queue)} events")
        
        # Run simulation with periodic updates
        while is_running and simulation.current_time < simulation.config.duration:
            # Process events
            if simulation.event_queue:
                # Use heapq.heappop to maintain priority queue order
                event_time, _, event = heapq.heappop(simulation.event_queue)
                simulation.current_time = event_time
                simulation._process_event(event)
                simulation._record_market_state()
                
                # Schedule next event from the agent that just acted
                if hasattr(event, 'trader_id'):
                    for agent_type, agent_list in simulation.agents.items():
                        for agent in agent_list:
                            if agent.trader_id == event.trader_id:
                                next_event = agent.get_next_event(simulation.current_time)
                                if next_event:
                                    # Add a unique counter to break ties
                                    heapq.heappush(simulation.event_queue, (next_event.timestamp, time.time(), next_event))
                                break
            else:
                # If no events, advance time and schedule new events
                simulation.current_time += 1.0
                for agent_type, agent_list in simulation.agents.items():
                    for agent in agent_list:
                        next_event = agent.get_next_event(simulation.current_time)
                        if next_event:
                            heapq.heappush(simulation.event_queue, (next_event.timestamp, time.time(), next_event))
            
            # Debug time progression
            if simulation.current_time % 10 < 0.1:  # Print every ~10 seconds
                print(f"Simulation time: {simulation.current_time:.1f}s, Events in queue: {len(simulation.event_queue)}")
                if simulation.trades:
                    print(f"Last trade time: {simulation.trades[-1].timestamp:.1f}s")
            
            # Emit update via WebSocket
            emit_update()
            time.sleep(0.1)  # Update every 100ms
        
        # Final update
        emit_update()
        is_running = False
        
    except Exception as e:
        print(f"Simulation error: {e}")
        import traceback
        traceback.print_exc()
        is_running = False


def emit_update():
    """Emit simulation update via WebSocket."""
    global simulation
    
    if simulation is None:
        return
    
    try:
        # Get current order book state
        orderbook_state = simulation.get_orderbook_snapshot()
        
        # Get recent price history
        recent_prices = simulation.price_history[-100:] if simulation.price_history else []
        print(f"Price history length: {len(simulation.price_history)}, Recent prices: {len(recent_prices)}")
        
        # Get recent trades
        recent_trades = simulation.trades[-50:] if simulation.trades else []
        
        # Prepare update data
        update_data = {
            'timestamp': simulation.current_time,
            'orderbook': orderbook_state,
            'price_history': recent_prices,
            'recent_trades': [
                {
                    'trade_id': trade.trade_id,
                    'price': trade.price,
                    'quantity': trade.quantity,
                    'timestamp': trade.timestamp
                }
                for trade in recent_trades
            ],
            'metrics': {
                'timestamp': simulation.current_time,
                'num_trades': len(simulation.trades),
                'num_orders': len(simulation.order_events),
                'mid_price': simulation.mid_price,
                'spread': simulation.best_ask - simulation.best_bid,
                'best_bid': simulation.best_bid,
                'best_ask': simulation.best_ask
            },
            'strategy_performance': simulation.get_all_strategy_performance()
        }
        
        socketio.emit('simulation_update', update_data)
        
    except Exception as e:
        print(f"Error emitting update: {e}")


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to LOB Simulation'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client."""
    emit_update()


if __name__ == '__main__':
    print("Starting LOB Simulation Web Application...")
    print("Open http://localhost:8080 in your browser")
    socketio.run(app, debug=True, host='0.0.0.0', port=8080) 