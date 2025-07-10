# Project Architecture & Logic

## Overview

This project is a modular, extensible Python framework for simulating market microstructure and limit order book (LOB) dynamics. It supports both a web interface and a CLI, and is designed for research, experimentation, and extension.

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
└── examples/             # Example scripts
```

---

## Plugin/Registry System

- **Agents, Strategies, Metrics**: Each is a plugin, registered via a central registry in their respective submodules (`__init__.py`).
- **Adding New Plugins**: Create a new file for your agent/strategy/metric, subclass the appropriate base class, and register it in the registry.
- **Benefits**: No need to modify core code to add new types. Promotes extensibility and clean separation.

---

## Event-Driven Simulation Flow

- **Initialization**: Loads config, sets up agents, strategies, order book, and event queue.
- **Event Loop**: Processes events (orders, trades, cancels) in time order. Agents and strategies generate new events based on market state.
- **Market Data**: Order book state, price history, and trades are tracked and updated at each step.
- **Metrics**: Market, liquidity, and impact metrics are calculated and available for analysis.

---

## Order Book Modularization

- **orderbook/order.py**: Order dataclass
- **orderbook/book.py**: Main OrderBook class
- **orderbook/matching.py**: Matching engine logic
- **orderbook/state.py**: State, serialization, and snapshot logic
- **orderbook/utils.py**: Utilities (if needed)

---

## Adding New Components

- **Agent**: Add a new file in `lob_simulation/agents/`, subclass `BaseAgent`, register in `__init__.py`.
- **Strategy**: Add a new file in `lob_simulation/strategies/`, subclass `BaseStrategy`, register in `__init__.py`.
- **Metric**: Add a new file in `lob_simulation/metrics/`, subclass `BaseMetrics`, register in `__init__.py`.
- **Event**: Add a new file in `lob_simulation/events/`, subclass `Event`, register in `__init__.py`.

---

## Configuration & Environment

- All configuration is managed in `config/settings.py`.
- Can be overridden via environment variables (see `settings.py` for details).
- Use the CLI `config` command to view, save, or load configs.

---

## Testing & Examples

- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Simulation tests**: `tests/test_simulation.py`
- **Examples**: `examples/` contains scripts for basic simulation, market impact analysis, strategy comparison, etc.

---

## Web & CLI Integration

- **Web**: Flask + SocketIO app in `lob_simulation/web/app.py`. Start with `python app.py`.
- **CLI**: Modular CLI in `lob_simulation/cli/main.py`. Start with `python main.py` or `python -m lob_simulation.cli.main`.
- Both interfaces use the same simulation engine and plugin system.

---

## Best Practices

- Keep each agent, strategy, metric, and event in its own file for clarity.
- Register all plugins in the appropriate `__init__.py` registry.
- Use the provided base classes and interfaces for consistency.
- Write tests for new components in `tests/`.
- Document your code with clear docstrings and comments.

---

## Further Documentation

- See code docstrings and comments for detailed API documentation.
- Example scripts are in `examples/`.
- For advanced usage, see the modular submodules and their registries.

---

## License

This project is licensed under the MIT License. 