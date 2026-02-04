"""
Collectors module - contains all IP collectors.
"""
from .base import BaseCollector
from .ipsum import IpsumCollector
from .abuseipdb import AbuseIPDBCollector
from .cncert import CNCERTCollector


# Registry of all available collectors
COLLECTOR_REGISTRY = {
    'ipsum': IpsumCollector,
    'abuseipdb': AbuseIPDBCollector,
    'cncert': CNCERTCollector,
}


def get_collector(name: str, config: dict) -> BaseCollector:
    """
    Get a collector instance by name.
    
    Args:
        name: Collector name
        config: Collector configuration
        
    Returns:
        Collector instance
        
    Raises:
        ValueError: If collector not found
    """
    if name not in COLLECTOR_REGISTRY:
        raise ValueError(f"Collector '{name}' not found")
    
    return COLLECTOR_REGISTRY[name](config)


__all__ = [
    'BaseCollector',
    'IpsumCollector',
    'AbuseIPDBCollector',
    'CNCERTCollector',
    'COLLECTOR_REGISTRY',
    'get_collector',
]
