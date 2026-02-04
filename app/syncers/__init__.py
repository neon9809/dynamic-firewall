"""
Syncers module - contains all router syncers.
"""
from .base import BaseSyncer
from .unifi import UniFiSyncer


# Registry of all available syncers
SYNCER_REGISTRY = {
    'unifi': UniFiSyncer,
}


def get_syncer(name: str, config: dict) -> BaseSyncer:
    """
    Get a syncer instance by name.
    
    Args:
        name: Syncer name
        config: Syncer configuration
        
    Returns:
        Syncer instance
        
    Raises:
        ValueError: If syncer not found
    """
    if name not in SYNCER_REGISTRY:
        raise ValueError(f"Syncer '{name}' not found")
    
    return SYNCER_REGISTRY[name](config)


__all__ = [
    'BaseSyncer',
    'UniFiSyncer',
    'SYNCER_REGISTRY',
    'get_syncer',
]
