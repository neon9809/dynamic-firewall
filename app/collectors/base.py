"""
Base collector class for all IP collectors.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import logging


class BaseCollector(ABC):
    """
    Abstract base class for all collectors.
    Each collector must implement the fetch() method.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the collector with configuration.
        
        Args:
            config: Configuration dictionary for this collector
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.logger = logging.getLogger(f"collector.{self.name}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this collector."""
        pass

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch malicious IPs from the data source.
        
        Returns:
            List of dictionaries containing IP information:
            [
                {
                    'ip': '1.2.3.4',
                    'source': 'ipsum',
                    'score': 5,
                    'last_seen': datetime.now()
                },
                ...
            ]
        """
        pass

    def is_enabled(self) -> bool:
        """Check if this collector is enabled."""
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
