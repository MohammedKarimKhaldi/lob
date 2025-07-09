"""
Command-line interface for the LOB simulation.
Modular CLI with different commands and options.
"""

import argparse
import sys
from typing import Optional

from config.settings import get_config, load_config_from_env
from lob_simulation.utils.logger import get_logger
from lob_simulation.web.app import run_web_app
from lob_simulation.core.simulation import LimitOrderBookSimulation


class CLI:
    """Command-line interface for the LOB simulation."""
    
    def __init__(self):
        self.logger = get_logger("cli")
        self.config = get_config()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Limit Order Book Simulation CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s web                    # Start web interface
  %(prog)s run --duration 3600    # Run simulation for 1 hour
  %(prog)s test --strategies mm   # Test market making strategy
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Web command
        web_parser = subparsers.add_parser('web', help='Start web interface')
        web_parser.add_argument('--host', default=None, help='Host to bind to')
        web_parser.add_argument('--port', type=int, default=None, help='Port to bind to')
        web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Run simulation')
        run_parser.add_argument('--duration', type=float, default=3600.0, help='Simulation duration in seconds')
        run_parser.add_argument('--strategies', nargs='+', default=['market_making'], help='Strategies to run')
        run_parser.add_argument('--output', help='Output file for results')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test strategies')
        test_parser.add_argument('--strategies', nargs='+', default=['market_making'], help='Strategies to test')
        test_parser.add_argument('--duration', type=float, default=600.0, help='Test duration in seconds')
        test_parser.add_argument('--output', help='Output file for results')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument('--show', action='store_true', help='Show current configuration')
        config_parser.add_argument('--save', help='Save configuration to file')
        config_parser.add_argument('--load', help='Load configuration from file')
        
        return parser
    
    def run_web(self, args) -> None:
        """Run the web interface."""
        self.logger.info("Starting web interface...")
        run_web_app(host=args.host, port=args.port, debug=args.debug)
    
    def run_simulation(self, args) -> None:
        """Run a simulation."""
        self.logger.info(f"Running simulation for {args.duration} seconds...")
        
        # Initialize simulation
        sim = LimitOrderBookSimulation()
        
        # Add strategies
        for strategy_name in args.strategies:
            config = {
                'initial_capital': self.config.agent.initial_capital,
                'max_position': self.config.agent.max_position
            }
            sim.add_strategy(strategy_name, config)
        
        # Run simulation
        sim.run(duration=args.duration)
        
        # Get results
        results = sim.get_results()
        
        # Save results if output file specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Results saved to {args.output}")
        
        # Print summary
        self._print_simulation_summary(results)
    
    def test_strategies(self, args) -> None:
        """Test strategies."""
        self.logger.info(f"Testing strategies: {args.strategies}")
        
        results = {}
        for strategy_name in args.strategies:
            self.logger.info(f"Testing strategy: {strategy_name}")
            
            # Initialize simulation
            sim = LimitOrderBookSimulation()
            
            # Add single strategy
            config = {
                'initial_capital': self.config.agent.initial_capital,
                'max_position': self.config.agent.max_position
            }
            sim.add_strategy(strategy_name, config)
            
            # Run simulation
            sim.run(duration=args.duration)
            
            # Get performance
            performance = sim.get_strategy_performance(strategy_name)
            results[strategy_name] = performance
        
        # Save results if output file specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Test results saved to {args.output}")
        
        # Print comparison
        self._print_strategy_comparison(results)
    
    def manage_config(self, args) -> None:
        """Manage configuration."""
        if args.show:
            self._show_config()
        elif args.save:
            self.config.save_to_file(args.save)
            self.logger.info(f"Configuration saved to {args.save}")
        elif args.load:
            self.config.load_from_file(args.load)
            self.logger.info(f"Configuration loaded from {args.load}")
        else:
            self._show_config()
    
    def _show_config(self) -> None:
        """Show current configuration."""
        config_data = self.config.get_all_config()
        import json
        print(json.dumps(config_data, indent=2))
    
    def _print_simulation_summary(self, results: dict) -> None:
        """Print simulation summary."""
        print("\n=== Simulation Summary ===")
        print(f"Duration: {results.get('duration', 'N/A')} seconds")
        print(f"Total trades: {len(results.get('trades', []))}")
        print(f"Final price: {results.get('final_price', 'N/A')}")
        print(f"Price volatility: {results.get('volatility', 'N/A')}")
        
        if 'strategies' in results:
            print("\nStrategy Performance:")
            for strategy_name, performance in results['strategies'].items():
                print(f"  {strategy_name}:")
                print(f"    PnL: {performance.get('pnl', 'N/A')}")
                print(f"    Sharpe Ratio: {performance.get('sharpe_ratio', 'N/A')}")
                print(f"    Max Drawdown: {performance.get('max_drawdown', 'N/A')}")
    
    def _print_strategy_comparison(self, results: dict) -> None:
        """Print strategy comparison."""
        print("\n=== Strategy Comparison ===")
        
        # Create comparison table
        headers = ['Strategy', 'PnL', 'Sharpe Ratio', 'Max Drawdown', 'Win Rate']
        rows = []
        
        for strategy_name, performance in results.items():
            rows.append([
                strategy_name,
                f"{performance.get('pnl', 0):.2f}",
                f"{performance.get('sharpe_ratio', 0):.3f}",
                f"{performance.get('max_drawdown', 0):.2f}",
                f"{performance.get('win_rate', 0):.1%}"
            ])
        
        # Print table
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
        
        # Header
        header_str = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
        print(header_str)
        print("-" * len(header_str))
        
        # Rows
        for row in rows:
            print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))
    
    def run(self, args: Optional[list] = None) -> None:
        """Run the CLI."""
        # Load configuration from environment
        load_config_from_env()
        
        # Parse arguments
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        try:
            # Execute command
            if parsed_args.command == 'web':
                self.run_web(parsed_args)
            elif parsed_args.command == 'run':
                self.run_simulation(parsed_args)
            elif parsed_args.command == 'test':
                self.test_strategies(parsed_args)
            elif parsed_args.command == 'config':
                self.manage_config(parsed_args)
            else:
                parser.print_help()
                
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli = CLI()
    cli.run()


if __name__ == '__main__':
    main() 