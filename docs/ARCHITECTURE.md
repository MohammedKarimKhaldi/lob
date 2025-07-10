# Codebase Documentation: Modular LOB Simulation

This document provides a comprehensive overview of the codebase, describing the purpose, structure, and extensibility of each major module and submodule. It is intended for developers and contributors.

---

## 1. `lob_simulation/agents/`

**Purpose:** Implements market agents (participants) and the agent plugin/registry system.

- **`base.py`**: Defines the abstract base class for all agents.
  ```python
  class BaseAgent(ABC):
      def get_next_event(self, current_time: float) -> Optional[Event]: ...
      def process_market_data(self, market_data: Dict[str, Any]): ...
  ```
- **Types:**
  - `InformedTrader`, `UninformedTrader`, `MarketMaker` (each in its own file)
- **Registry:**
  - `__init__.py` provides a registry for agent types:
    ```python
    agent_registry.register('market_maker', MarketMaker)
    agent_registry.create('market_maker', ...)
    ```
- **Extending:**
  - Add a new agent by subclassing `BaseAgent` and registering it in the registry.

---

## 2. `lob_simulation/strategies/`

**Purpose:** Implements trading strategies and the strategy plugin/registry system.

- **`base.py`**: Abstract base class for all strategies, plus config and performance dataclasses.
  ```python
  class BaseStrategy(ABC):
      def generate_orders(self, current_time: float, market_data: Dict[str, Any]) -> List[OrderEvent]: ...
      def update_market_data(self, market_data: Dict[str, Any]): ...
      def process_trade(self, trade: TradeEvent): ...
  ```
- **Types:**
  - `MarketMakingStrategy`, `MomentumStrategy`, `MeanReversionStrategy`, `ArbitrageStrategy`
- **Registry:**
  - `__init__.py` provides a registry for strategy types:
    ```python
    strategy_registry.register('momentum', MomentumStrategy)
    strategy_registry.create('momentum', config)
    ```
- **Extending:**
  - Add a new strategy by subclassing `BaseStrategy` and registering it in the registry.

---

## 3. `lob_simulation/metrics/`

**Purpose:** Implements market metrics and the metrics plugin/registry system.

- **`base.py`**: Abstract base class for all metrics calculators.
  ```python
  class BaseMetrics(ABC):
      def calculate(self, *args, **kwargs) -> None: ...
      def get_summary(self) -> Dict[str, Any]: ...
  ```
- **Types:**
  - `MarketMetrics`, `LiquidityMetrics`, `ImpactMetrics`
- **Registry:**
  - `__init__.py` provides a registry for metrics types:
    ```python
    metrics_registry.register('market', MarketMetrics)
    metrics_registry.create('market')
    ```
- **Extending:**
  - Add a new metrics class by subclassing `BaseMetrics` and registering it in the registry.

---

## 4. `lob_simulation/events/`

**Purpose:** Defines all event types and the event queue for the simulation.

- **`base.py`**: Abstract base class for all events.
  ```python
  class Event(ABC):
      def process(self) -> Any: ...
  class EventType(Enum): ...
  ```
- **Types:**
  - `OrderEvent`, `CancelEvent`, `TradeEvent`, `MarketDataEvent` (each in its own file)
- **Event Queue:**
  - `queue.py` implements a priority queue for events.
- **Extending:**
  - Add a new event by subclassing `Event` and registering it in `__init__.py`.

---

## 5. `lob_simulation/orderbook/`

**Purpose:** Implements the modular order book and matching engine.

- **`order.py`**: Defines the `Order` dataclass.
- **`book.py`**: Main `OrderBook` class.
  ```python
  class OrderBook:
      def add_order(self, order_event: OrderEvent, current_time: float = 0.0) -> List[TradeEvent]: ...
      def cancel_order(self, order_id: str) -> bool: ...
      def get_state(self) -> Dict[str, Any]: ...
  ```
- **`matching.py`**: Matching engine logic (order matching, price-time priority).
- **`state.py`**: State, serialization, and snapshot logic.
- **`utils.py`**: Utilities (if needed).
- **Extending:**
  - Add new order types, matching logic, or state serialization as needed.

---

## 6. `lob_simulation/core/`

**Purpose:** Simulation engine and abstract interfaces for extensibility.

- **`simulation.py`**: Main simulation engine.
  ```python
  class LimitOrderBookSimulation:
      def run(self, duration: Optional[float] = None) -> Dict[str, Any]: ...
      def add_strategy(self, strategy_name: str, config: StrategyConfig): ...
      def get_results(self) -> Dict[str, Any]: ...
  ```
- **`interfaces.py`**: Abstract interfaces for agents, strategies, metrics, simulation engine, etc.
  ```python
  class Strategy(ABC): ...
  class Agent(ABC): ...
  class MetricsCalculator(ABC): ...
  class SimulationEngine(ABC): ...
  ```
- **Extending:**
  - Implement new interfaces or extend the simulation engine for custom workflows.

---

## 7. `lob_simulation/cli/`

**Purpose:** Command-line interface for running simulations, testing strategies, and managing config.

- **`main.py`**: CLI entry point.
  - Commands: `web`, `run`, `test`, `config`
  - Example usage:
    ```bash
    python main.py run --duration 3600 --strategies market_making momentum
    python main.py config --show
    ```
- **Extending:**
  - Add new CLI commands or options in `main.py`.

---

## 8. `lob_simulation/web/`

**Purpose:** Web application (Flask + SocketIO) for interactive simulation and visualization.

- **`app.py`**: Web app entry point and main logic.
  - Endpoints:
    - `/` (main page)
    - `/api/start_simulation`, `/api/stop_simulation`, `/api/simulation_status`, `/api/order_book`, `/api/price_history`, `/api/trade_history`, `/api/strategy_performance`
  - WebSocket events for real-time updates.
- **Extending:**
  - Add new API endpoints or frontend features as needed.

---

## 9. `lob_simulation/utils/`

**Purpose:** Utilities for logging and shared functionality.

- **`logger.py`**: Centralized logging utilities.
  ```python
  class SimulationLogger:
      def info(self, message: str) -> None: ...
      def error(self, message: str) -> None: ...
  class LoggerMixin: ...
  def get_logger(name: str = "lob_simulation") -> SimulationLogger: ...
  ```
- **Extending:**
  - Add new utilities as needed for the codebase.

---

## How Modules Fit Together

- The **simulation engine** (`core/simulation.py`) orchestrates agents, strategies, the order book, and events.
- **Agents** and **strategies** are pluggable and interact via registries.
- **Events** drive the simulation, processed in time order.
- **Metrics** are calculated throughout the simulation for analysis.
- The **CLI** and **web app** provide user interfaces for running and visualizing simulations.

---

## Extending the Codebase

- Subclass the appropriate base class (agent, strategy, metric, event) and register in the registry.
- Add new CLI commands or web endpoints as needed.
- Write tests for new components in `tests/`.

---

## Further Reading

- See code docstrings and comments for detailed API documentation.
- Example scripts are in `examples/`.
- For configuration, see `config/settings.py`.

---

## License

This project is licensed under the MIT License. 