#!/usr/bin/env python3
"""
Main entry point for the LOB simulation.
Modular entry point that supports both web interface and CLI.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lob_simulation.cli.main import main as cli_main
from config.settings import load_config_from_env


def main():
    """Main entry point."""
    # Load configuration from environment
    load_config_from_env()
    
    # Run CLI
    cli_main()


if __name__ == '__main__':
    main() 