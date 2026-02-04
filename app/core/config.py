"""
Configuration management module.
"""
import os
import yaml
from typing import Dict, Any
import logging


class Config:
    """
    Configuration manager for dynamic-firewall.
    Loads configuration from YAML file and environment variables.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger("config")
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Replace environment variables
            config = self._replace_env_vars(config)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def _replace_env_vars(self, config: Any) -> Any:
        """
        Replace ${VAR_NAME} with environment variables.
        
        Args:
            config: Configuration value (can be dict, list, or string)
            
        Returns:
            Configuration with environment variables replaced
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            if config.startswith('${') and config.endswith('}'):
                var_name = config[2:-1]
                return os.getenv(var_name, config)
        return config

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'global': {
                'update_interval': 3600,
                'log_level': 'INFO',
                'db_path': 'data/ips.db'
            },
            'collectors': {},
            'syncers': {}
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def get_collectors_config(self) -> Dict[str, Any]:
        """
        Get collectors configuration.
        
        Returns:
            Collectors configuration dictionary
        """
        return self.data.get('collectors', {})

    def get_syncers_config(self) -> Dict[str, Any]:
        """
        Get syncers configuration.
        
        Returns:
            Syncers configuration dictionary
        """
        return self.data.get('syncers', {})

    def get_global_config(self) -> Dict[str, Any]:
        """
        Get global configuration.
        
        Returns:
            Global configuration dictionary
        """
        return self.data.get('global', {})
