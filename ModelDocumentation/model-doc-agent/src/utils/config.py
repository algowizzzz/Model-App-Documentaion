import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for Model Documentation Agent."""
    
    defaults = {
        "llm": {
            "model": "claude-3-opus-20240229",
            "temperature": 0.2,
            "max_tokens": 4096
        },
        "codebase": {
            "extensions": [".py", ".sql", ".json", ".yml", ".yaml"],
            "exclude_dirs": ["__pycache__", ".git", "venv", ".DS_Store"]
        },
        "debug": {
            "level": "INFO",
            "log_file": "model_doc_agent.log"
        },
        "parser": {
            "python": {
                "enabled": True
            }
        }
    }
    
    def __init__(self, config_path: str = None):
        """Initialize with default or custom config."""
        self.config = self.defaults.copy()
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load configuration from file."""
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    custom_config = json.load(f)
                self._update_nested_dict(self.config, custom_config)
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse config file {config_path}: {e}")
            except Exception as e:
                print(f"Warning: Error loading config file {config_path}: {e}")

    def _update_nested_dict(self, d: Dict, u: Dict):
        """Update nested dictionary."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by dot-notated key."""
        keys = key.split('.')
        value = self.config
        
        for k_part in keys:
            if isinstance(value, dict) and k_part in value:
                value = value[k_part]
            else:
                return default
                
        return value

# Global config instance (optional, can be instantiated where needed)
# global_config = Config() 