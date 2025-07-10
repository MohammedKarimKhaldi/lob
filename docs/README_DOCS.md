# Limit Order Book (LOB) Simulation Framework

A modular, extensible Python framework for simulating market microstructure and limit order book (LOB) dynamics. Designed for research, experimentation, and extensibility, with both a web interface and CLI.

---

## Features

- **Modular plugin architecture** for agents, strategies, metrics, and events
- **Event-driven simulation engine** with microsecond precision
- **Web interface** (Flask + SocketIO) for interactive simulation and visualization
- **Command-line interface (CLI)** for batch runs, testing, and configuration
- **Extensive metrics**: market, liquidity, impact, and more
- **Easy extensibility**: add new agents, strategies, metrics, or events with minimal code changes
- **Comprehensive tests and examples**

---

## Directory Structure

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
├── tests/                # Unit and integration tests
├── examples/             # Example scripts
└── docs/                 # Documentation (see ARCHITECTURE.md)
```

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

## Quick Start

### Web Interface
Start the web app:
```bash
python app.py [--host 0.0.0.0] [--port 8080] [--debug]
```
Open your browser at [http://localhost:8080](http://localhost:8080).

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
- `web` — Start the web interface
- `run` — Run a simulation
    - Example: `python main.py run --duration 3600 --strategies market_making momentum`
- `test` — Test strategies and compare performance
    - Example: `python main.py test --strategies market_making mean_reversion`
- `config` — Show, save, or load configuration
    - Example: `python main.py config --show`

---

## Usage Examples

### Web
- Select strategies, configure parameters, and visualize results interactively.

### CLI
- Run a simulation:
  ```bash
  python main.py run --duration 1800 --strategies market_making momentum
  ```
- Test strategies:
  ```bash
  python main.py test --strategies market_making mean_reversion
  ```

### In Code
- Import and use the simulation engine directly:
  ```python
  from lob_simulation.core.simulation import LimitOrderBookSimulation
  sim = LimitOrderBookSimulation()
  sim.add_strategy('market_making', {...})
  sim.run(duration=3600)
  results = sim.get_results()
  ```

---

## Codebase Structure & Module Guide

- **Agents**: `lob_simulation/agents/` — Market participants (base class, types, registry)
- **Strategies**: `lob_simulation/strategies/` — Trading strategies (base class, types, registry)
- **Metrics**: `lob_simulation/metrics/` — Market metrics (base class, types, registry)
- **Events**: `lob_simulation/events/` — Event types and event queue
- **Order Book**: `lob_simulation/orderbook/` — Order, OrderBook, matching, state, utils
- **Simulation Engine**: `lob_simulation/core/simulation.py` — Main simulation logic
- **Interfaces**: `lob_simulation/core/interfaces.py` — Abstract interfaces for extensibility
- **CLI**: `lob_simulation/cli/main.py` — Command-line interface
- **Web**: `lob_simulation/web/app.py` — Web app (Flask + SocketIO)
- **Utils**: `lob_simulation/utils/` — Logging and shared utilities

For a detailed module-by-module reference, see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md).

---

## How to Extend

- **Add a new agent/strategy/metric/event**: Subclass the appropriate base class and register in the registry (`__init__.py` of the submodule).
- **Order Book**: Extend or modify matching/state logic in `lob_simulation/orderbook/`.
- **CLI/Web**: Add new commands or endpoints as needed.
- **Write tests** for new components in `tests/`.

---

## Configuration & Environment

- All configuration is managed in `config/settings.py` and can be overridden via environment variables (see file for details).
- Use the CLI `config` command to view or save/load configs.

---

## Testing

- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Simulation tests**: `tests/test_simulation.py`
- Run all tests:
  ```bash
  pytest
  ```

---

## Contributing

Contributions are welcome! Please:
- Follow the modular structure and use base classes/registries
- Write clear docstrings and comments
- Add tests for new features
- Open a pull request with a clear description

---

## License

This project is licensed under the MIT License.

---

## Further Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): Detailed module-by-module codebase reference
- Code docstrings and comments
- Example scripts in `examples/`
- For questions, open an issue or discussion 