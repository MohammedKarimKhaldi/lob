#!/usr/bin/env python3
"""
Simple Demonstration of Limit Order Book Simulation

This script demonstrates the basic usage of the LOB simulation
with a minimal configuration and simple analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lob_simulation import LimitOrderBookSimulation, SimulationConfig


def main():
    """Run a simple demonstration simulation."""
    
    print("Limit Order Book Simulation - Simple Demo")
    print("=" * 50)
    
    # Create a simple configuration
    config = SimulationConfig(
        duration=60.0,  # 1 minute simulation
        initial_price=100.0,
        tick_size=0.01,
        max_levels=5,
        num_informed_traders=2,
        num_uninformed_traders=5,
        num_market_makers=1,
        lambda_informed=0.2,
        lambda_uninformed=0.3,
        lambda_market_maker=0.1
    )
    
    print("Configuration:")
    print(f"  Duration: {config.duration} seconds")
    print(f"  Initial Price: ${config.initial_price}")
    print(f"  Informed Traders: {config.num_informed_traders}")
    print(f"  Uninformed Traders: {config.num_uninformed_traders}")
    print(f"  Market Makers: {config.num_market_makers}")
    print()
    
    # Create and run simulation
    print("Running simulation...")
    simulation = LimitOrderBookSimulation(config)
    results = simulation.run()
    
    # Print results
    print("\nResults:")
    print(f"  Total Trades: {len(results['trades'])}")
    print(f"  Total Orders: {len(results['order_events'])}")
    print(f"  Final Mid Price: ${results['orderbook_state']['mid_price']:.2f}")
    print(f"  Final Spread: ${results['orderbook_state']['spread']:.4f}")
    
    # Show some recent trades
    if results['trades']:
        print("\nRecent Trades:")
        for trade in results['trades'][-5:]:  # Last 5 trades
            print(f"  {trade.trade_id}: {trade.quantity} shares at ${trade.price:.2f}")
    
    # Show order book depth
    depth = results['orderbook_state']['depth']
    print(f"\nOrder Book Depth:")
    print(f"  Bids: {depth['bids']}")
    print(f"  Asks: {depth['asks']}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main() 