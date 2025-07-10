# Core Simulation Engine & Interfaces Documentation

This module implements the main simulation engine and all abstract interfaces for extensibility.

---

## SimulationConfig

```python
@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    duration: float = 3600.0
    tick_size: float = 0.01
    max_levels: int = 10
    initial_price: float = 100.0
    volatility: float = 0.02
    mean_reversion: float = 0.1
    num_informed_traders: int = 5
    num_uninformed_traders: int = 20
    num_market_makers: int = 3
    lambda_informed: float = 0.1
    lambda_uninformed: float = 0.5
    lambda_market_maker: float = 0.2
    impact_lambda: float = 0.1
    impact_gamma: float = 0.5
    temp_decay_tau: float = 300.0
    cancel_half_life: float = 60.0
    market_order_alpha: float = 1.0
    market_order_s0: float = 0.01
```
- Used to configure all aspects of the simulation.

---

## LimitOrderBookSimulation

```python
class LimitOrderBookSimulation:
    """Main simulation engine for limit order book dynamics."""
    def run(self, duration: Optional[float] = None) -> Dict[str, Any]
    def add_strategy(self, strategy_name: str, config: StrategyConfig)
    def get_results(self) -> Dict[str, Any]
    def get_strategy_performance(self, strategy_name: str) -> Dict[str, Any]
    def get_all_strategy_performance(self) -> Dict[str, Dict[str, Any]]
    def add_custom_event(self, event: Event)
    def reset(self)
    def run_step(self, max_events: int = 10)
    def stop(self)
```
- Orchestrates agents, strategies, order book, and events.
- Provides methods to run the simulation, add strategies, and retrieve results.

---

## Abstract Interfaces

### Strategy
```python
class Strategy(ABC):
    def generate_orders(self, market_data: Dict[str, Any]) -> List[Any]
    def update_market_data(self, market_data: Dict[str, Any]) -> None
    def process_trade(self, trade: Any) -> None
    def get_performance(self) -> Dict[str, Any]
```

### Agent
```python
class Agent(ABC):
    def get_next_event(self, current_time: float) -> Optional[Any]
    def process_market_update(self, market_data: Dict[str, Any]) -> None
```

### MetricsCalculator
```python
class MetricsCalculator(ABC):
    def calculate_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]
    def reset(self) -> None
```

### SimulationEngine
```python
class SimulationEngine(ABC):
    def start(self, config: Dict[str, Any]) -> None
    def stop(self) -> None
    def step(self, max_events: int = 10) -> None
    def get_status(self) -> Dict[str, Any]
    def get_market_data(self) -> Dict[str, Any]
```

---

## Example Usage

```python
from lob_simulation.core.simulation import LimitOrderBookSimulation
sim = LimitOrderBookSimulation()
sim.add_strategy('market_making', {...})
sim.run(duration=3600)
results = sim.get_results()
```

---

## Extending
- To add a new simulation engine, subclass `SimulationEngine` and implement required methods.
- To add new interfaces, define new abstract base classes in `interfaces.py`.

---

## Reference
- The core simulation engine is used by both the CLI and web app to run all simulations. 