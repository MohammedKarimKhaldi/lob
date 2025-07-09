"""
Command Line Interface for Limit Order Book Simulation

This module provides a CLI for running simulations and generating reports.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

from .simulation import LimitOrderBookSimulation, SimulationConfig


def create_config_from_args(args) -> SimulationConfig:
    """Create simulation configuration from command line arguments."""
    return SimulationConfig(
        duration=args.duration,
        initial_price=args.initial_price,
        tick_size=args.tick_size,
        max_levels=args.max_levels,
        num_informed_traders=args.informed_traders,
        num_uninformed_traders=args.uninformed_traders,
        num_market_makers=args.market_makers,
        lambda_informed=args.lambda_informed,
        lambda_uninformed=args.lambda_uninformed,
        lambda_market_maker=args.lambda_market_maker,
        impact_lambda=args.impact_lambda,
        impact_gamma=args.impact_gamma,
        temp_decay_tau=args.temp_decay_tau,
        cancel_half_life=args.cancel_half_life
    )


def save_results(results: Dict[str, Any], output_dir: str):
    """Save simulation results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    with open(output_path / "config.json", "w") as f:
        json.dump(results['config'].__dict__, f, indent=2)
    
    # Save trades
    if results['trades']:
        trades_data = [trade.__dict__ for trade in results['trades']]
        with open(output_path / "trades.json", "w") as f:
            json.dump(trades_data, f, indent=2)
    
    # Save price history
    if results['price_history']:
        with open(output_path / "price_history.json", "w") as f:
            json.dump(results['price_history'], f, indent=2)
    
    # Save spread history
    if results['spread_history']:
        with open(output_path / "spread_history.json", "w") as f:
            json.dump(results['spread_history'], f, indent=2)
    
    # Save volume history
    if results['volume_history']:
        with open(output_path / "volume_history.json", "w") as f:
            json.dump(results['volume_history'], f, indent=2)
    
    # Save metrics
    if results['metrics']:
        with open(output_path / "metrics.json", "w") as f:
            json.dump(results['metrics'], f, indent=2)
    
    # Save liquidity metrics
    if results['liquidity_metrics']:
        with open(output_path / "liquidity_metrics.json", "w") as f:
            json.dump(results['liquidity_metrics'], f, indent=2)
    
    # Save impact metrics
    if results['impact_metrics']:
        with open(output_path / "impact_metrics.json", "w") as f:
            json.dump(results['impact_metrics'], f, indent=2)
    
    print(f"Results saved to: {output_path}")


def print_summary(results: Dict[str, Any]):
    """Print a summary of simulation results."""
    print("\n" + "="*60)
    print("SIMULATION SUMMARY")
    print("="*60)
    
    # Basic statistics
    print(f"Duration: {results['config'].duration:.1f} seconds")
    print(f"Initial Price: ${results['config'].initial_price:.2f}")
    print(f"Final Mid Price: ${results['orderbook_state']['mid_price']:.2f}")
    print(f"Final Spread: ${results['orderbook_state']['spread']:.4f}")
    print()
    
    # Trade statistics
    print(f"Total Trades: {len(results['trades'])}")
    print(f"Total Orders: {len(results['order_events'])}")
    if len(results['trades']) > 0:
        print(f"Trade Frequency: {len(results['trades']) / results['config'].duration:.2f} trades/sec")
    print()
    
    # Market metrics
    if results['metrics']:
        metrics = results['metrics']
        print("MARKET METRICS:")
        print(f"  Price Volatility: {metrics.get('price_metrics', {}).get('volatility', 0):.4f}")
        print(f"  Average Spread: ${metrics.get('spread_metrics', {}).get('avg_spread', 0):.4f}")
        print(f"  Trade Frequency: {metrics.get('trade_metrics', {}).get('trade_frequency', 0):.2f} trades/sec")
        print()
    
    # Liquidity metrics
    if results['liquidity_metrics']:
        liq_metrics = results['liquidity_metrics']
        print("LIQUIDITY METRICS:")
        print(f"  Average Depth: {liq_metrics.get('depth_metrics', {}).get('avg_depth', 0):.0f}")
        print(f"  Depth Imbalance: {liq_metrics.get('depth_metrics', {}).get('depth_imbalance', 0):.3f}")
        print(f"  Resilience Score: {liq_metrics.get('resilience_metrics', {}).get('resilience_score', 0):.3f}")
        print()
    
    # Impact metrics
    if results['impact_metrics']:
        impact_metrics = results['impact_metrics']
        print("IMPACT METRICS:")
        print(f"  Temporary Impact: {impact_metrics.get('impact_coefficients', {}).get('temporary_impact', 0):.6f}")
        print(f"  Permanent Impact: {impact_metrics.get('impact_coefficients', {}).get('permanent_impact', 0):.6f}")
        print(f"  Decay Rate: {impact_metrics.get('impact_coefficients', {}).get('decay_rate', 0):.3f}")
        print()
    
    print("="*60)


def run_simulation(args):
    """Run the simulation with given arguments."""
    print("Limit Order Book Simulation")
    print("="*40)
    
    # Create configuration
    config = create_config_from_args(args)
    
    print(f"Configuration:")
    print(f"  Duration: {config.duration} seconds")
    print(f"  Initial Price: ${config.initial_price}")
    print(f"  Informed Traders: {config.num_informed_traders}")
    print(f"  Uninformed Traders: {config.num_uninformed_traders}")
    print(f"  Market Makers: {config.num_market_makers}")
    print()
    
    # Initialize and run simulation
    print("Running simulation...")
    simulation = LimitOrderBookSimulation(config)
    results = simulation.run()
    
    # Print summary
    print_summary(results)
    
    # Save results if output directory specified
    if args.output:
        save_results(results, args.output)
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Limit Order Book Simulation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic simulation
  lob-sim run

  # Run with custom parameters
  lob-sim run --duration 1800 --initial-price 50.0 --informed-traders 10

  # Run and save results
  lob-sim run --output results/ --duration 3600

  # Run with high-frequency trading parameters
  lob-sim run --tick-size 0.001 --lambda-informed 1.0 --lambda-uninformed 2.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run simulation')
    
    # Time parameters
    run_parser.add_argument(
        '--duration', '-d',
        type=float,
        default=3600.0,
        help='Simulation duration in seconds (default: 3600)'
    )
    
    # Market parameters
    run_parser.add_argument(
        '--initial-price', '-p',
        type=float,
        default=100.0,
        help='Initial price (default: 100.0)'
    )
    run_parser.add_argument(
        '--tick-size', '-t',
        type=float,
        default=0.01,
        help='Tick size (default: 0.01)'
    )
    run_parser.add_argument(
        '--max-levels', '-l',
        type=int,
        default=10,
        help='Maximum order book levels (default: 10)'
    )
    
    # Agent parameters
    run_parser.add_argument(
        '--informed-traders', '-i',
        type=int,
        default=5,
        help='Number of informed traders (default: 5)'
    )
    run_parser.add_argument(
        '--uninformed-traders', '-u',
        type=int,
        default=20,
        help='Number of uninformed traders (default: 20)'
    )
    run_parser.add_argument(
        '--market-makers', '-m',
        type=int,
        default=3,
        help='Number of market makers (default: 3)'
    )
    
    # Arrival rates
    run_parser.add_argument(
        '--lambda-informed',
        type=float,
        default=0.1,
        help='Informed trader arrival rate (default: 0.1)'
    )
    run_parser.add_argument(
        '--lambda-uninformed',
        type=float,
        default=0.5,
        help='Uninformed trader arrival rate (default: 0.5)'
    )
    run_parser.add_argument(
        '--lambda-market-maker',
        type=float,
        default=0.2,
        help='Market maker activity rate (default: 0.2)'
    )
    
    # Impact parameters
    run_parser.add_argument(
        '--impact-lambda',
        type=float,
        default=0.1,
        help='Linear impact coefficient (default: 0.1)'
    )
    run_parser.add_argument(
        '--impact-gamma',
        type=float,
        default=0.5,
        help='Impact exponent (default: 0.5)'
    )
    run_parser.add_argument(
        '--temp-decay-tau',
        type=float,
        default=300.0,
        help='Temporary impact decay time (default: 300.0)'
    )
    
    # Cancellation parameters
    run_parser.add_argument(
        '--cancel-half-life',
        type=float,
        default=60.0,
        help='Order cancellation half-life (default: 60.0)'
    )
    
    # Output parameters
    run_parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for results'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'run':
        try:
            run_simulation(args)
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        except Exception as e:
            print(f"Error running simulation: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main() 