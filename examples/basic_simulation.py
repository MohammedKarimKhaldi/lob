"""
Basic Limit Order Book Simulation Example

This example demonstrates the core functionality of the LOB simulation
with a simple configuration and basic analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lob_simulation import LimitOrderBookSimulation, SimulationConfig
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def run_basic_simulation():
    """Run a basic simulation with default parameters."""
    
    print("Starting Basic LOB Simulation...")
    print("=" * 50)
    
    # Create simulation configuration
    config = SimulationConfig(
        duration=300.0,  # 5 minutes
        initial_price=100.0,
        tick_size=0.01,
        max_levels=10,
        num_informed_traders=3,
        num_uninformed_traders=10,
        num_market_makers=2,
        lambda_informed=0.2,
        lambda_uninformed=0.5,
        lambda_market_maker=0.3
    )
    
    print(f"Configuration:")
    print(f"  Duration: {config.duration} seconds")
    print(f"  Initial Price: ${config.initial_price}")
    print(f"  Informed Traders: {config.num_informed_traders}")
    print(f"  Uninformed Traders: {config.num_uninformed_traders}")
    print(f"  Market Makers: {config.num_market_makers}")
    print()
    
    # Initialize and run simulation
    simulation = LimitOrderBookSimulation(config)
    results = simulation.run()
    
    # Print results summary
    print("Simulation Results:")
    print("=" * 50)
    print(f"Total Trades: {len(results['trades'])}")
    print(f"Total Orders: {len(results['order_events'])}")
    print(f"Final Mid Price: ${results['orderbook_state']['mid_price']:.2f}")
    print(f"Final Spread: ${results['orderbook_state']['spread']:.4f}")
    print()
    
    # Print metrics
    if results['metrics']:
        metrics = results['metrics']
        print("Market Metrics:")
        print(f"  Price Volatility: {metrics.get('price_metrics', {}).get('volatility', 0):.4f}")
        print(f"  Average Spread: ${metrics.get('spread_metrics', {}).get('avg_spread', 0):.4f}")
        print(f"  Trade Frequency: {metrics.get('trade_metrics', {}).get('trade_frequency', 0):.2f} trades/sec")
        print()
    
    return results


def analyze_results(results):
    """Analyze simulation results and create visualizations."""
    
    print("Creating Visualizations...")
    print("=" * 50)
    
    # Convert data to DataFrames
    price_df = pd.DataFrame(results['price_history'])
    spread_df = pd.DataFrame(results['spread_history'])
    volume_df = pd.DataFrame(results['volume_history'])
    
    if len(results['trades']) > 0:
        trades_df = pd.DataFrame([trade.__dict__ for trade in results['trades']])
    else:
        trades_df = pd.DataFrame()
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Limit Order Book Simulation Results', fontsize=16)
    
    # 1. Price Evolution
    if len(price_df) > 0:
        axes[0, 0].plot(price_df['timestamp'], price_df['mid_price'], 'b-', label='Mid Price')
        axes[0, 0].plot(price_df['timestamp'], price_df['best_bid'], 'g-', alpha=0.7, label='Best Bid')
        axes[0, 0].plot(price_df['timestamp'], price_df['best_ask'], 'r-', alpha=0.7, label='Best Ask')
        axes[0, 0].set_xlabel('Time (seconds)')
        axes[0, 0].set_ylabel('Price ($)')
        axes[0, 0].set_title('Price Evolution')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Spread Evolution
    if len(spread_df) > 0:
        axes[0, 1].plot(spread_df['timestamp'], spread_df['spread'], 'purple')
        axes[0, 1].set_xlabel('Time (seconds)')
        axes[0, 1].set_ylabel('Spread ($)')
        axes[0, 1].set_title('Bid-Ask Spread Evolution')
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Volume at Best Bid/Ask
    if len(volume_df) > 0:
        axes[1, 0].plot(volume_df['timestamp'], volume_df['bid_volume'], 'g-', label='Bid Volume')
        axes[1, 0].plot(volume_df['timestamp'], volume_df['ask_volume'], 'r-', label='Ask Volume')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Volume')
        axes[1, 0].set_title('Volume at Best Bid/Ask')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Trade Distribution
    if len(trades_df) > 0:
        axes[1, 1].hist(trades_df['price'], bins=20, alpha=0.7, color='orange')
        axes[1, 1].set_xlabel('Trade Price ($)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Trade Price Distribution')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('basic_simulation_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualization saved as 'basic_simulation_results.png'")
    print()


def create_animated_gif(results):
    """Create an animated GIF showing the evolution of the order book."""
    
    print("Creating Animated GIF...")
    print("=" * 50)
    
    try:
        import imageio
        from matplotlib.animation import FuncAnimation
        import matplotlib.pyplot as plt
        
        # Sample data at regular intervals
        price_df = pd.DataFrame(results['price_history'])
        if len(price_df) == 0:
            print("No price data available for animation")
            return
        
        # Create frames for animation
        frames = []
        step = max(1, len(price_df) // 50)  # 50 frames max
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for i in range(0, len(price_df), step):
            # Clear previous plot
            ax.clear()
            
            # Plot price evolution up to current point
            current_data = price_df.iloc[:i+1]
            if len(current_data) > 0:
                ax.plot(current_data['timestamp'], current_data['mid_price'], 'b-', linewidth=2)
                ax.plot(current_data['timestamp'], current_data['best_bid'], 'g-', alpha=0.7)
                ax.plot(current_data['timestamp'], current_data['best_ask'], 'r-', alpha=0.7)
            
            # Set plot properties
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Price ($)')
            ax.set_title(f'Price Evolution - Time: {price_df.iloc[i]["timestamp"]:.1f}s')
            ax.grid(True, alpha=0.3)
            
            # Set consistent y-axis limits
            if len(price_df) > 0:
                price_range = price_df['mid_price'].max() - price_df['mid_price'].min()
                margin = price_range * 0.1
                ax.set_ylim(
                    price_df['mid_price'].min() - margin,
                    price_df['mid_price'].max() + margin
                )
            
            # Save frame
            plt.tight_layout()
            plt.savefig(f'temp_frame_{i:04d}.png', dpi=100, bbox_inches='tight')
            frames.append(imageio.imread(f'temp_frame_{i:04d}.png'))
            
            # Clean up temporary file
            import os
            os.remove(f'temp_frame_{i:04d}.png')
        
        # Create GIF
        imageio.mimsave('price_evolution.gif', frames, fps=5)
        plt.close()
        
        print("Animated GIF saved as 'price_evolution.gif'")
        
    except ImportError:
        print("imageio not available. Install with: pip install imageio")
    except Exception as e:
        print(f"Error creating animated GIF: {e}")


def main():
    """Main function to run the basic simulation example."""
    
    print("Limit Order Book Simulation - Basic Example")
    print("=" * 60)
    print()
    
    # Run simulation
    results = run_basic_simulation()
    
    # Analyze results
    analyze_results(results)
    
    # Create animated visualization
    create_animated_gif(results)
    
    print("Basic simulation example completed!")
    print("Check the generated files:")
    print("  - basic_simulation_results.png")
    print("  - price_evolution.gif")


if __name__ == "__main__":
    main() 