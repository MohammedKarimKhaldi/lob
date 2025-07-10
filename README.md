# Modular Limit Order Book (LOB) Simulation

An extensible and fully modular Python framework for simulating market microstructure and limit order book (LOB) dynamics. Includes a web interface and CLI for interactive and automated experimentation.

---

## Project Structure

```
lob/
├── app.py                # Main web entry point
├── main.py               # Main CLI entry point
├── requirements.txt      # Python dependencies
├── setup.py              # Packaging and install
├── config/
│   └── settings.py       # Centralized configuration
├── lob_simulation/
│   ├── agents/           # Agent plugins (e.g., InformedTrader, MarketMaker)
│   ├── strategies/       # Strategy plugins (e.g., market making, momentum)
│   ├── metrics/          # Metrics plugins (market, liquidity, impact)
│   ├── events/           # Event types (OrderEvent, TradeEvent, etc.)
│   ├── orderbook/        # Modular order book (Order, OrderBook, matching, state)
│   ├── core/             # Simulation engine and interfaces
│   ├── cli/              # CLI entry point and logic
│   ├── web/              # Web app (Flask + SocketIO)
│   ├── utils/            # Utilities (logging, etc.)
│   └── ...
├── static/               # Web static assets
├── templates/            # Web HTML templates
└── tests/                # Unit and integration tests
```

---

## Modular Plugin Architecture

- **Agents, Strategies, Metrics**: Each type is a plugin, registered via a central registry. Add new types by creating a new file and registering the class.
- **Order Book**: Split into submodules for order data, book logic, matching, state, and utilities.
- **Events**: Each event type (order, trade, cancel, etc.) is a separate class for clarity and extensibility.
- **Simulation Engine**: Event-driven, agent-based, and supports microsecond precision. Strategies and agents interact via clean interfaces.

### Example: Adding a New Strategy
1. Create a new file in `lob_simulation/strategies/` (e.g., `my_strategy.py`).
2. Implement your strategy class, inheriting from `BaseStrategy`.
3. Register it in the registry in `lob_simulation/strategies/__init__.py`.

---

## Simulation Logic Overview

- **Initialization**: Loads configuration, sets up agents, strategies, order book, and event queue.
- **Event Loop**: Processes events (orders, trades, cancels) in time order. Agents and strategies generate new events based on market state.
- **Market Data**: Order book state, price history, and trades are tracked and updated at each step.
- **Metrics**: Market, liquidity, and impact metrics are calculated and available for analysis.
- **Extensibility**: All major components (agents, strategies, metrics, events, order book) are modular and pluggable.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd lob
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   (Or use `pip install .` for editable/development mode.)

---

## Running the Simulation

### Web Interface

Start the web app (Flask + SocketIO):
```bash
python app.py [--host 0.0.0.0] [--port 8080] [--debug]
```
- Open your browser at [http://localhost:8080](http://localhost:8080) (or your chosen host/port).
- Interactively select strategies, run simulations, and visualize results.

### Command-Line Interface (CLI)

Run the CLI for batch simulations, testing, or config management:
```bash
python main.py [command] [options]
```
Or directly:
```bash
python -m lob_simulation.cli.main [command] [options]
```

#### CLI Commands
- `web` — Start the web interface (same as above)
- `run` — Run a simulation
    - Example: `python main.py run --duration 3600 --strategies market_making momentum`
- `test` — Test strategies and compare performance
    - Example: `python main.py test --strategies market_making mean_reversion`
- `config` — Show, save, or load configuration
    - Example: `python main.py config --show`

---

## Configuration & Environment

- All configuration is managed in `config/settings.py` and can be overridden via environment variables (see file for details).
- Example environment variables:
    - `LOB_INITIAL_PRICE`, `LOB_SIMULATION_DURATION`, `LOB_HOST`, `LOB_PORT`, `LOB_DEBUG`, etc.
- Use the CLI `config` command to view or save/load configs.

---

## Extending the Codebase

- **Add a new agent/strategy/metric/event**: Create a new file in the appropriate submodule and register it in the registry.
- **Order Book**: Extend or modify matching/state logic in `lob_simulation/orderbook/`.
- **Metrics**: Add new metrics calculators in `lob_simulation/metrics/`.
- **Web/CLI**: Add new endpoints or commands as needed.

---

## Best Practices

- Keep each agent, strategy, metric, and event in its own file for clarity.
- Register all plugins in the appropriate `__init__.py` registry.
- Use the provided base classes and interfaces for consistency.
- Write tests for new components in `tests/`.

---

## Further Documentation

- See code docstrings and comments for detailed API documentation.
- Example scripts are in `examples/`.
- For advanced usage, see the modular submodules and their registries.

---

## License

This project is licensed under the MIT License. 