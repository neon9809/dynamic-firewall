"""
Base syncer class for all router syncers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseSyncer(ABC):
    """
    Abstract base class for all syncers.
    Each syncer must implement the sync() method.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the syncer with configuration.
        
        Args:
            config: Configuration dictionary for this syncer
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.logger = logging.getLogger(f"syncer.{self.name}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this syncer."""
        pass

    @abstractmethod
    def sync(self, ips: List[str]) -> bool:
        """
        Sync malicious IPs to the router firewall.
        
        Args:
            ips: List of IP addresses to block
            
        Returns:
            True if sync was successful, False otherwise
        """
        pass

    def is_enabled(self) -> bool:
        """Check if this syncer is enabled."""
        return self.enabled

    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(f"[{self.name}] {message}")
