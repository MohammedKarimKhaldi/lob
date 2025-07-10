# CLI Module Documentation

This module implements the command-line interface for running simulations, testing strategies, and managing configuration.

---

## CLI Class

```python
class CLI:
    """Command-line interface for the LOB simulation."""
    def create_parser(self) -> argparse.ArgumentParser
    def run_web(self, args) -> None
    def run_simulation(self, args) -> None
    def test_strategies(self, args) -> None
    def manage_config(self, args) -> None
    def run(self, args: Optional[list] = None) -> None
```
- Handles all CLI commands and argument parsing.
- Provides methods to start the web app, run simulations, test strategies, and manage config.

---

## Main Commands

- `web` — Start the web interface
- `run` — Run a simulation
    - Example: `python main.py run --duration 3600 --strategies market_making momentum`
- `test` — Test strategies and compare performance
    - Example: `python main.py test --strategies market_making mean_reversion`
- `config` — Show, save, or load configuration
    - Example: `python main.py config --show`

---

## Example Usage

```bash
python main.py run --duration 1800 --strategies market_making momentum
python main.py test --strategies market_making mean_reversion
python main.py config --show
```

---

## Extending
- To add a new CLI command, add a new subparser in `create_parser` and implement the corresponding method in the `CLI` class.

---

## Reference
- The CLI is used as the main entry point for batch simulations and configuration management. 