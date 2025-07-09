#!/usr/bin/env python3
"""
Simple test script to verify strategies are working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lob_simulation import (
    LimitOrderBookSimulation, SimulationConfig, 
    StrategyConfig, create_strategy
)

def test_strategies():
    """Test that strategies can be created and configured."""
    
    print("Testing Strategy Framework...")
    
    # Test 1: Create strategies
    print("\n1. Creating strategies...")
    
    strategies = [
        ('market_making', StrategyConfig(strategy_name='market_making', max_position=100)),
        ('momentum', StrategyConfig(strategy_name='momentum', max_position=100)),
        ('mean_reversion', StrategyConfig(strategy_name='mean_reversion', max_position=100)),
        ('arbitrage', StrategyConfig(strategy_name='arbitrage', max_position=100))
    ]
    
    for name, config in strategies:
        try:
            strategy = create_strategy(name, config)
            print(f"✓ {name} strategy created successfully")
        except Exception as e:
            print(f"✗ Failed to create {name} strategy: {e}")
    
    # Test 2: Create simulation with strategies
    print("\n2. Testing simulation with strategies...")
    
    sim_config = SimulationConfig(
        duration=60.0,  # 1 minute test
        initial_price=100.0,
        tick_size=0.01,
        max_levels=5,
        num_informed_traders=2,
        num_uninformed_traders=5,
        num_market_makers=1
    )
    
    simulation = LimitOrderBookSimulation(sim_config)
    
    # Add strategies
    for name, config in strategies:
        simulation.add_strategy(name, config)
        print(f"✓ Added {name} strategy to simulation")
    
    # Test 3: Run simulation
    print("\n3. Running simulation...")
    try:
        results = simulation.run()
        print("✓ Simulation completed successfully")
        
        # Test 4: Get strategy performance
        print("\n4. Checking strategy performance...")
        performance = simulation.get_all_strategy_performance()
        
        for strategy_name, perf in performance.items():
            print(f"✓ {strategy_name}: PnL=${perf['total_pnl']:.2f}, Trades={perf['num_trades']}")
            
    except Exception as e:
        print(f"✗ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nStrategy test completed!")

if __name__ == "__main__":
    test_strategies() 