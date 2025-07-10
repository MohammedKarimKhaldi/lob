#!/usr/bin/env python3
"""
Main entry point for the LOB simulation web application.
Uses the modular web interface.
"""

import sys
import os
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import load_config_from_env
from lob_simulation.web.app import run_web_app


def main():
    """Main entry point for the web application."""
    # Load configuration from environment
    load_config_from_env()
    
    parser = argparse.ArgumentParser(description="LOB Simulation Web App")
    parser.add_argument('--host', type=str, default=None, help='Host to run the server on')
    parser.add_argument('--port', type=int, default=None, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Run the web application with optional host/port/debug
    run_web_app(host=args.host, port=args.port, debug=args.debug if args.debug else None)


if __name__ == '__main__':
    main() 