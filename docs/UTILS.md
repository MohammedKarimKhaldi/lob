# Utils Module Documentation

This module provides logging utilities and shared functionality for the simulation framework.

---

## SimulationLogger

```python
class SimulationLogger:
    """Centralized logger for the LOB simulation."""
    def debug(self, message: str) -> None
    def info(self, message: str) -> None
    def warning(self, message: str) -> None
    def error(self, message: str) -> None
    def critical(self, message: str) -> None
    def exception(self, message: str) -> None
```
- Provides centralized logging with support for console and file output.
- Configured via `config/settings.py`.

---

## LoggerMixin

```python
class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    def log_debug(self, message: str) -> None
    def log_info(self, message: str) -> None
    def log_warning(self, message: str) -> None
    def log_error(self, message: str) -> None
    def log_exception(self, message: str) -> None
```
- Add to any class to enable logging with the class name as the logger.

---

## get_logger, setup_logging

```python
def get_logger(name: str = "lob_simulation") -> SimulationLogger
def setup_logging(name: str = "lob_simulation") -> SimulationLogger
```
- Use to get or set up a logger instance.

---

## Example Usage

```python
from lob_simulation.utils.logger import get_logger, LoggerMixin

logger = get_logger()
logger.info("Simulation started")

class MyClass(LoggerMixin):
    def do_something(self):
        self.log_info("Doing something")
```

---

## Extending
- Add new utility functions or classes in `utils/` as needed.

---

## Reference
- Logging is used throughout the codebase for debugging, info, and error reporting. 