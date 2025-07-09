"""
Logging utilities for the LOB simulation.
Centralized logging configuration and utilities.
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from config.settings import get_config


class SimulationLogger:
    """Centralized logger for the LOB simulation."""
    
    def __init__(self, name: str = "lob_simulation"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the logger with configuration."""
        config = get_config()
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, config.logging.level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(config.logging.format)
        
        # Console handler
        if config.logging.console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if config.logging.file:
            file_path = Path(config.logging.file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(config.logging.file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message)


# Global logger instance
_simulation_logger: Optional[SimulationLogger] = None


def get_logger(name: str = "lob_simulation") -> SimulationLogger:
    """Get the global logger instance."""
    global _simulation_logger
    if _simulation_logger is None:
        _simulation_logger = SimulationLogger(name)
    return _simulation_logger


def setup_logging(name: str = "lob_simulation") -> SimulationLogger:
    """Setup and return a new logger instance."""
    return SimulationLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def log_exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message) 