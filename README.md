# Limit Order Book Simulation

A comprehensive market microstructure modeling framework for simulating limit order book dynamics, analyzing trading strategies, and studying price impact and liquidity provision mechanisms.

## 🎯 Overview

This project implements a sophisticated agent-based modeling framework for financial markets, featuring:

- **Multi-agent simulation** with informed/uninformed traders and market makers
- **Trading strategy framework** with market making, momentum, mean reversion, and arbitrage strategies
- **Real-time web visualization** with interactive charts and live updates
- **Advanced price formation mechanisms** with temporary and permanent impact
- **Event-driven simulation engine** with priority queue processing
- **Market quality metrics** and liquidity analysis
- **Strategy performance tracking** with PnL and risk metrics

## 🏗️ Architecture

### Core Components

1. **Agent-Based Modeling Framework**
   - Informed Traders (Poisson process λ_I)
   - Uninformed Traders (Noise trading λ_U)
   - Market Makers (Bid-ask spread optimization)

2. **Trading Strategy Framework**
   - Market Making Strategy (inventory management)
   - Momentum Strategy (trend following)
   - Mean Reversion Strategy (contrarian)
   - Arbitrage Strategy (statistical arbitrage)

3. **Order Flow Dynamics**
   - Limit order arrival: λ(δ) = Ae^(-kδ)
   - Market order probability: P(market) = 1/(1 + e^(-α(S-S₀)))
   - Cancellation rate: Exponential decay with τ_cancel

4. **Price Formation Mechanism**
   - Linear market impact: Δp = λ × sign(Q) × Q^γ
   - Temporary impact decay: I(t) = I₀ × e^(-t/τ)
   - Mean reversion and noise for realistic price dynamics

5. **Event-Driven Simulation Engine**
   - Priority queue for event processing
   - Microsecond precision timing
   - Real-time market state updates

6. **Market Quality Metrics**
   - Liquidity measures (spread, depth, resilience)
   - Price impact analysis (square-root law)
   - Strategy performance metrics

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
pip install -r requirements.txt
```

### Web Interface (Recommended)

```bash
# Start the web application
python app.py

# Open http://localhost:8080 in your browser
```

The web interface provides:
- Real-time order book visualization
- Live price charts
- Strategy performance monitoring
- Interactive simulation controls
- Trade history and analytics

### Programmatic Usage

```python
from lob_simulation import LimitOrderBookSimulation, StrategyConfig

# Initialize simulation with strategies
config = StrategyConfig(
    strategy_name="market_making",
    initial_capital=100000.0,
    max_position=1000
)

sim = LimitOrderBookSimulation()
sim.add_strategy("market_making", config)

# Run simulation
sim.run(duration=3600)  # 1 hour simulation

# Analyze results
results = sim.get_results()
strategy_performance = sim.get_strategy_performance("market_making")
```

### Strategy Comparison

```python
# Compare multiple strategies
strategies = [
    {"name": "market_making", "params": {"initial_capital": 100000}},
    {"name": "momentum", "params": {"initial_capital": 100000}},
    {"name": "mean_reversion", "params": {"initial_capital": 100000}}
]

# Run comparison
python examples/strategy_comparison.py
```

## 📊 Features

### Real-time Visualization
- Interactive order book depth chart
- Live price evolution with D3.js
- Real-time trade updates
- Strategy performance dashboard
- Market maker inventory tracking

### Trading Strategy Framework
- **Market Making**: Bid-ask spread optimization with inventory management
- **Momentum**: Trend-following based on price momentum
- **Mean Reversion**: Contrarian strategy based on price deviations
- **Arbitrage**: Statistical arbitrage opportunities

### Advanced Analytics
- Market impact analysis
- Liquidity provision metrics
- Order flow imbalance detection
- Strategy PnL tracking
- Risk metrics (Sharpe ratio, drawdown, win rate)

### Simulation Capabilities
- Event-driven engine with priority queue
- Real-time market state updates
- Configurable market participant behaviors
- Realistic market microstructure modeling
- Strategy integration and performance tracking

## 📁 Project Structure

```
lob/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── app.py                   # Web application entry point
├── lob_simulation/          # Core simulation engine
│   ├── __init__.py
│   ├── simulation.py        # Main simulation engine
│   ├── agents.py            # Market participant models
│   ├── orderbook.py         # Order book implementation
│   ├── events.py            # Event system
│   ├── strategies.py        # Trading strategy framework
│   ├── metrics.py           # Market quality metrics
│   └── utils.py             # Utility functions
├── static/                  # Web assets (CSS, JS)
├── templates/               # HTML templates
└── examples/                # Usage examples
```

## 🔬 Research Applications

### Market Microstructure Analysis
- Bid-ask spread dynamics
- Order flow patterns
- Market maker behavior
- Price discovery process

### Trading Strategy Development
- Market making algorithms
- Liquidity provision strategies
- Impact minimization techniques
- High-frequency trading simulation

### Risk Management
- Market impact assessment
- Liquidity risk modeling
- Order execution analysis
- Portfolio optimization

## 📈 Visualization Examples

The simulation generates various visualizations:

1. **Order Book Depth Chart**: Real-time bid/ask levels with volume
2. **Price Evolution**: Mid-price and trade prices over time
3. **Strategy Performance**: PnL, positions, and risk metrics
4. **Market Impact Analysis**: Price impact vs. order size
5. **Liquidity Metrics**: Spread, depth, and resilience measures

## 🎮 Interactive Features

### Web Interface Controls
- Start/Stop simulation
- Adjust simulation parameters
- Select trading strategies
- Real-time performance monitoring
- Export results

### Strategy Configuration
- Initial capital allocation
- Position limits
- Risk parameters
- Strategy-specific settings

## 🐛 Recent Fixes

- ✅ Fixed event queue processing with proper priority queue implementation
- ✅ Resolved simulation time advancement issues
- ✅ Fixed strategy PnL tracking and performance metrics
- ✅ Corrected order book updates and trade execution
- ✅ Improved real-time visualization with proper data flow
- ✅ Fixed agent event scheduling and time progression

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 📚 References

- O'Hara, M. (1995). Market Microstructure Theory
- Bouchaud, J.P. (2010). Price Impact
- Cont, R. (2011). Statistical Modeling of High-Frequency Financial Data
- Avellaneda, M. (2008). Market Making and Inventory Control

## 🆘 Support

For questions and support, please open an issue on GitHub. 