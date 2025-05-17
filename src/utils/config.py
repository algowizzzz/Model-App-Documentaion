"""
Configuration management for the Model Documentation Agent.
"""

import os
import json
from typing import Dict, Any, Optional, Union

class Config:
    """
    Configuration manager for the Model Documentation Agent.
    
    Handles loading configuration from environment variables,
    default values, and optionally from config files.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            config_file: Optional path to a JSON config file.
        """
        self.config = {
            # Default LLM settings
            "llm": {
                "model_name": "claude-3-haiku-20240307",
                "temperature": 0.2,
                "max_tokens": 4096,
                "mock_mode": True  # Default to mock mode for safety
            },
            # Default agent settings
            "agent": {
                "verbose": True,
                "max_iterations": 15
            },
            # Default parser settings
            "parser": {
                "parse_chunks": True
            }
        }
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    self._update_nested_dict(self.config, file_config)
            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")
    
    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Update a nested dictionary with another nested dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with new values
            
        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "llm.temperature")
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value or the default if not found
        """
        parts = key_path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "llm.temperature")
            value: Value to set
        """
        parts = key_path.split('.')
        config = self.config
        
        for i, part in enumerate(parts[:-1]):
            if part not in config:
                config[part] = {}
            config = config[part]
            
        config[parts[-1]] = value 