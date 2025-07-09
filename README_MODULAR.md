# LOB Simulation - Modular Architecture

This document describes the new modular architecture of the Limit Order Book (LOB) simulation system.

## 🏗️ Modular Structure

The project has been restructured into a modular architecture with clear separation of concerns:

```
lob/
├── main.py                    # Main entry point
├── app.py                     # Web application entry point
├── config/                    # Configuration management
│   └── settings.py           # Centralized configuration
├── lob_simulation/           # Core simulation engine
│   ├── core/                 # Core simulation components
│   │   ├── __init__.py
│   │   └── simulation.py     # Main simulation engine
│   ├── web/                  # Web interface
│   │   ├── __init__.py
│   │   └── app.py           # Flask web application
│   ├── cli/                  # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py          # CLI implementation
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   └── logger.py        # Logging utilities
│   ├── agents.py             # Market participant models
│   ├── orderbook.py          # Order book implementation
│   ├── events.py             # Event system
│   ├── strategies.py         # Trading strategy framework
│   └── metrics.py            # Market quality metrics
├── static/                   # Web assets
│   ├── css/
│   │   └── main.css         # Modular CSS
│   ├── js/
│   │   └── app.js           # Modular JavaScript
│   └── images/              # UI screenshots
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Main page
│   └── components/          # Reusable components
│       ├── header.html
│       ├── control_panel.html
│       └── dashboard.html
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   │   └── test_config.py
│   └── integration/        # Integration tests
└── docs/                   # Documentation
    └── images/             # Documentation images
```

## 🔧 Key Modules

### 1. Configuration Management (`config/`)

**Purpose**: Centralized configuration management for all simulation parameters.

**Features**:
- Type-safe configuration classes using dataclasses
- Environment variable support
- JSON file import/export
- Validation and error handling

**Usage**:
```python
from config.settings import get_config

config = get_config()
print(f"Initial price: {config.simulation.initial_price}")
print(f"Web port: {config.web.port}")
```

### 2. Core Simulation (`lob_simulation/core/`)

**Purpose**: Core simulation engine and business logic.

**Components**:
- `simulation.py`: Main simulation engine
- Event-driven architecture
- Agent-based modeling
- Strategy framework integration

### 3. Web Interface (`lob_simulation/web/`)

**Purpose**: Modular Flask web application with WebSocket support.

**Features**:
- RESTful API endpoints
- Real-time WebSocket updates
- Background simulation processing
- Error handling and logging

**Usage**:
```python
from lob_simulation.web.app import run_web_app

run_web_app(host='0.0.0.0', port=8080, debug=True)
```

### 4. Command-Line Interface (`lob_simulation/cli/`)

**Purpose**: Command-line interface for simulation control and testing.

**Commands**:
- `web`: Start web interface
- `run`: Run simulation with specified parameters
- `test`: Test strategies and compare performance
- `config`: Manage configuration

**Usage**:
```bash
# Start web interface
python main.py web --port 8080

# Run simulation
python main.py run --duration 3600 --strategies market_making momentum

# Test strategies
python main.py test --strategies market_making momentum --duration 600

# Show configuration
python main.py config --show
```

### 5. Utilities (`lob_simulation/utils/`)

**Purpose**: Shared utilities and helper functions.

**Components**:
- `logger.py`: Centralized logging with configuration support
- `LoggerMixin`: Mixin class for adding logging to any class

**Usage**:
```python
from lob_simulation.utils.logger import get_logger, LoggerMixin

# Get logger
logger = get_logger("my_module")
logger.info("Application started")

# Use mixin
class MyClass(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.log_info("MyClass initialized")
```

### 6. Frontend Assets (`static/`)

**Purpose**: Modular frontend assets with separation of concerns.

**Components**:
- `css/main.css`: Modular CSS with component-based styling
- `js/app.js`: Modular JavaScript with separate managers for different functionalities

**Features**:
- Component-based CSS architecture
- Modular JavaScript with clear separation of concerns
- Responsive design
- Real-time updates via WebSocket

### 7. Templates (`templates/`)

**Purpose**: Modular HTML templates using Jinja2 templating.

**Structure**:
- `base.html`: Base template with common layout
- `index.html`: Main dashboard page
- `components/`: Reusable template components

**Features**:
- Template inheritance
- Component-based architecture
- Clean separation of concerns

## 🚀 Usage Examples

### Web Interface

```bash
# Start web interface
python app.py

# Or use CLI
python main.py web --host 0.0.0.0 --port 8080 --debug
```

### Programmatic Usage

```python
from lob_simulation.core.simulation import LimitOrderBookSimulation
from config.settings import get_config

# Get configuration
config = get_config()

# Initialize simulation
sim = LimitOrderBookSimulation()

# Add strategies
sim.add_strategy("market_making", {
    'initial_capital': config.agent.initial_capital,
    'max_position': config.agent.max_position
})

# Run simulation
sim.run(duration=config.simulation.simulation_duration)
```

### Configuration Management

```python
from config.settings import get_config, load_config_from_env

# Load from environment variables
load_config_from_env()

# Get configuration
config = get_config()

# Update configuration
config.update_config('simulation', initial_price=150.0)
config.update_config('web', port=9090)

# Save to file
config.save_to_file('my_config.json')
```

### Logging

```python
from lob_simulation.utils.logger import get_logger

# Get logger
logger = get_logger("my_module")

# Use logger
logger.info("Application started")
logger.warning("Configuration warning")
logger.error("Error occurred")
```

## 🧪 Testing

The modular structure includes a comprehensive test suite:

```bash
# Run unit tests
python -m pytest tests/unit/

# Run specific test
python -m pytest tests/unit/test_config.py

# Run with coverage
python -m pytest tests/ --cov=lob_simulation --cov=config
```

## 🔄 Migration from Old Structure

The old monolithic structure has been preserved for backward compatibility, but new development should use the modular structure:

### Old Structure (Deprecated)
```
lob_simulation/
├── simulation.py    # Monolithic simulation
├── agents.py        # Agent models
├── orderbook.py     # Order book
└── strategies.py    # Strategies
```

### New Structure (Recommended)
```
lob_simulation/
├── core/           # Core simulation engine
├── web/            # Web interface
├── cli/            # Command-line interface
├── utils/          # Utilities
└── [legacy files]  # Preserved for compatibility
```

## 📈 Benefits of Modular Architecture

1. **Separation of Concerns**: Each module has a single responsibility
2. **Reusability**: Components can be reused across different interfaces
3. **Testability**: Each module can be tested independently
4. **Maintainability**: Easier to maintain and update individual components
5. **Scalability**: Easy to add new features without affecting existing code
6. **Configuration Management**: Centralized configuration with multiple sources
7. **Error Handling**: Consistent error handling across modules
8. **Logging**: Centralized logging with configuration support

## 🔧 Development Guidelines

1. **Module Independence**: Each module should be independent and testable
2. **Configuration**: Use the centralized configuration system
3. **Logging**: Use the logging utilities for consistent logging
4. **Error Handling**: Implement proper error handling in each module
5. **Documentation**: Document all public interfaces
6. **Testing**: Write tests for each module
7. **Type Hints**: Use type hints for better code documentation

## 🚀 Future Enhancements

The modular architecture enables easy addition of new features:

1. **API Module**: RESTful API for external integrations
2. **Database Module**: Persistent storage for simulation results
3. **Analytics Module**: Advanced analytics and reporting
4. **Backtesting Module**: Historical data backtesting
5. **Risk Management Module**: Advanced risk management features
6. **Machine Learning Module**: ML-based trading strategies 