#!/usr/bin/env python3
"""
Strategy Comparison Example

This script demonstrates different trading strategies and compares their PnL performance
in the LOB simulation environment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from lob_simulation import (
    LimitOrderBookSimulation, SimulationConfig, 
    StrategyConfig, create_strategy
)


def run_strategy_comparison():
    """Run comparison of different trading strategies."""
    
    print("=== LOB Strategy Comparison ===")
    print(f"Started at: {datetime.now()}")
    
    # Simulation configuration
    sim_config = SimulationConfig(
        duration=300.0,  # 5 minutes
        initial_price=100.0,
        tick_size=0.01,
        max_levels=10,
        num_informed_traders=3,
        num_uninformed_traders=15,
        num_market_makers=2,
        lambda_informed=0.1,
        lambda_uninformed=0.3,
        lambda_market_maker=0.2
    )
    
    # Strategy configurations
    strategies = [
        {
            'name': 'market_making',
            'config': StrategyConfig(
                strategy_name='market_making',
                initial_capital=100000.0,
                max_position=500,
                max_order_size=50,
                min_spread=0.01,
                max_spread=0.05
            )
        },
        {
            'name': 'momentum',
            'config': StrategyConfig(
                strategy_name='momentum',
                initial_capital=100000.0,
                max_position=300,
                max_order_size=30,
                lookback_period=15,
                momentum_threshold=0.015
            )
        },
        {
            'name': 'mean_reversion',
            'config': StrategyConfig(
                strategy_name='mean_reversion',
                initial_capital=100000.0,
                max_position=300,
                max_order_size=30,
                lookback_period=25,
                mean_reversion_threshold=0.025
            )
        },
        {
            'name': 'arbitrage',
            'config': StrategyConfig(
                strategy_name='arbitrage',
                initial_capital=100000.0,
                max_position=200,
                max_order_size=20,
                arbitrage_threshold=0.008
            )
        }
    ]
    
    # Initialize simulation
    simulation = LimitOrderBookSimulation(sim_config)
    
    # Add strategies
    for strategy in strategies:
        simulation.add_strategy(strategy['name'], strategy['config'])
        print(f"Added strategy: {strategy['name']}")
    
    # Run simulation
    print("\nRunning simulation...")
    results = simulation.run()
    
    # Get strategy performance
    strategy_performance = simulation.get_all_strategy_performance()
    
    # Display results
    print("\n=== Strategy Performance Summary ===")
    print(f"{'Strategy':<15} {'Total PnL':<12} {'Win Rate':<10} {'Sharpe':<8} {'Max DD':<8} {'Trades':<8}")
    print("-" * 70)
    
    performance_data = []
    for strategy_name, perf in strategy_performance.items():
        print(f"{strategy_name:<15} "
              f"${perf['total_pnl']:<11.2f} "
              f"{perf['win_rate']:<10.2%} "
              f"{perf['sharpe_ratio']:<8.2f} "
              f"{perf['max_drawdown']:<8.2%} "
              f"{perf['num_trades']:<8}")
        
        performance_data.append({
            'strategy': strategy_name,
            'total_pnl': perf['total_pnl'],
            'win_rate': perf['win_rate'],
            'sharpe_ratio': perf['sharpe_ratio'],
            'max_drawdown': perf['max_drawdown'],
            'num_trades': perf['num_trades'],
            'realized_pnl': perf['realized_pnl'],
            'unrealized_pnl': perf['unrealized_pnl']
        })
    
    # Create visualizations
    create_performance_plots(performance_data, results)
    
    return strategy_performance, results


def create_performance_plots(performance_data, simulation_results):
    """Create performance comparison plots."""
    
    # Convert to DataFrame
    df = pd.DataFrame(performance_data)
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Trading Strategy Performance Comparison', fontsize=16, fontweight='bold')
    
    # 1. Total PnL Comparison
    ax1 = axes[0, 0]
    bars = ax1.bar(df['strategy'], df['total_pnl'], 
                   color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
    ax1.set_title('Total PnL by Strategy', fontweight='bold')
    ax1.set_ylabel('PnL ($)')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.1f}', ha='center', va='bottom' if height > 0 else 'top')
    
    # 2. Risk-Return Scatter Plot
    ax2 = axes[0, 1]
    scatter = ax2.scatter(df['max_drawdown'], df['total_pnl'], 
                         s=df['num_trades']*2, c=df['sharpe_ratio'], 
                         cmap='RdYlGn', alpha=0.7)
    ax2.set_xlabel('Maximum Drawdown')
    ax2.set_ylabel('Total PnL ($)')
    ax2.set_title('Risk-Return Profile', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add strategy labels
    for i, strategy in enumerate(df['strategy']):
        ax2.annotate(strategy, (df['max_drawdown'].iloc[i], df['total_pnl'].iloc[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Sharpe Ratio')
    
    # 3. Win Rate vs Number of Trades
    ax3 = axes[1, 0]
    bars = ax3.bar(df['strategy'], df['win_rate'], 
                   color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
    ax3.set_title('Win Rate by Strategy', fontweight='bold')
    ax3.set_ylabel('Win Rate')
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1%}', ha='center', va='bottom')
    
    # 4. PnL Components (Realized vs Unrealized)
    ax4 = axes[1, 1]
    x = np.arange(len(df))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, df['realized_pnl'], width, 
                    label='Realized PnL', color='#2E86AB', alpha=0.8)
    bars2 = ax4.bar(x + width/2, df['unrealized_pnl'], width, 
                    label='Unrealized PnL', color='#A23B72', alpha=0.8)
    
    ax4.set_xlabel('Strategy')
    ax4.set_ylabel('PnL ($)')
    ax4.set_title('PnL Components', fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(df['strategy'])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height != 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.1f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"strategy_comparison_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nPerformance plots saved as: {filename}")
    
    # Show the plot
    plt.show()


def create_pnl_timeline_plot(simulation_results):
    """Create PnL timeline plot for all strategies."""
    
    # Extract PnL history for each strategy
    # This would require modifying the simulation to track PnL over time
    # For now, we'll create a simple example
    
    plt.figure(figsize=(12, 8))
    
    # Simulate PnL timeline (in a real implementation, this would come from the simulation)
    time_points = np.linspace(0, 300, 100)
    
    strategies = ['market_making', 'momentum', 'mean_reversion', 'arbitrage']
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    for i, strategy in enumerate(strategies):
        # Simulate PnL path (replace with actual data from simulation)
        pnl_path = np.cumsum(np.random.normal(0, 0.5, len(time_points)))
        plt.plot(time_points, pnl_path, label=strategy, color=colors[i], linewidth=2)
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Cumulative PnL ($)')
    plt.title('Strategy PnL Timeline', fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pnl_timeline_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"PnL timeline saved as: {filename}")
    
    plt.show()


if __name__ == "__main__":
    try:
        strategy_performance, results = run_strategy_comparison()
        
        # Create additional visualizations
        create_pnl_timeline_plot(results)
        
        print("\n=== Analysis Complete ===")
        print("Strategy comparison completed successfully!")
        
    except Exception as e:
        print(f"Error running strategy comparison: {e}")
        import traceback
        traceback.print_exc() 