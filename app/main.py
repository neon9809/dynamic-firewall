#!/usr/bin/env python3
"""
dynamic-firewall - Automatic malicious IP synchronization to router firewalls.

Author: Manus AI
License: MIT
"""
import sys
import argparse
from core.engine import Engine


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='dynamic-firewall - Sync malicious IPs to router firewalls'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='/app/config/config.yaml',
        help='Path to configuration file (default: /app/config/config.yaml)'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (no scheduling)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='dynamic-firewall 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize engine
        engine = Engine(config_path=args.config)
        
        if args.once:
            # Run once and exit
            engine.run_once()
        else:
            # Run with scheduler
            engine.start()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
