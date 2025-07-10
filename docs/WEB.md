# Web Module Documentation

This module implements the web application (Flask + SocketIO) for interactive simulation and visualization.

---

## WebApplication Class

```python
class WebApplication(LoggerMixin):
    """Modular web application for the LOB simulation."""
    def __init__(self)
    def _setup_routes(self) -> None
    def _setup_socketio_events(self) -> None
    def _run_simulation_loop(self) -> None
    def _broadcast_market_update(self) -> None
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None) -> None
```
- Manages the Flask app, SocketIO server, and simulation lifecycle.
- Provides methods to set up routes, handle WebSocket events, and run the simulation loop.

---

## Main API Endpoints

- `/` — Main page (renders the frontend)
- `/api/start_simulation` — Start a new simulation (POST)
- `/api/stop_simulation` — Stop the simulation (POST)
- `/api/simulation_status` — Get simulation status (GET)
- `/api/order_book` — Get current order book state (GET)
- `/api/price_history` — Get price history (GET)
- `/api/trade_history` — Get trade history (GET)
- `/api/strategy_performance` — Get strategy performance (GET)

---

## WebSocket Events

- `connect` — Client connects
- `disconnect` — Client disconnects
- `request_update` — Client requests a market update
- `market_update` — Server sends market update to clients

---

## Example Usage

```bash
python app.py --host 0.0.0.0 --port 8080 --debug
# Open http://localhost:8080 in your browser
```

---

## Extending
- To add a new API endpoint, add a new route in `_setup_routes`.
- To add new WebSocket events, add handlers in `_setup_socketio_events`.
- To add new frontend features, update the templates and static files.

---

## Reference
- The web app is used as the main entry point for interactive simulation and visualization. 