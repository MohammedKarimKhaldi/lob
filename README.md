# Modular Limit Order Book (LOB) Simulation

## Modular Architecture

The codebase is now fully modular and professional, with the following structure:

- `lob_simulation/agents/` — Each agent type (e.g., InformedTrader, MarketMaker) in its own file, with a plugin registry.
- `lob_simulation/strategies/` — Each strategy (e.g., market making, momentum) in its own file, with a plugin registry.
- `lob_simulation/events/` — Each event type (OrderEvent, TradeEvent, etc.) in its own file, with a clean interface.
- `lob_simulation/metrics/` — Each metrics type (market, liquidity, impact) in its own file, with a plugin registry.
- `lob_simulation/orderbook/` — Fully modular order book:
    - `order.py` — Order dataclass
    - `book.py` — Main OrderBook class
    - `matching.py` — Matching engine logic
    - `state.py` — State, serialization, and snapshot logic
    - `utils.py` — Utilities (if needed)

## Strategy Initialization: Best Practices

- When starting a simulation, you can specify multiple strategies at startup.
- The backend now ensures that **all strategies are initialized, updated with the current market state, and their initial orders are scheduled into the event queue** before the simulation loop starts.
- This guarantees that all selected strategies are active and trading from the very first simulation step.

## Extending the Codebase

- To add a new agent, strategy, event, or metric, simply add a new file in the appropriate submodule and register it in the registry.
- The modular structure makes it easy to maintain, test, and extend the simulation engine.

## Running the Simulation

- Use the web interface or CLI to start a simulation with any combination of strategies.
- The system will handle initialization and event scheduling for all components in a robust, modular way. 