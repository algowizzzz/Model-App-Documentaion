import json
import os

def load_json_data(file_path: str):
    """Loads data from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Data file not found at {file_path}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded data from {file_path}")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while loading {file_path}: {e}")

def get_trades(config_dir: str = "config"):
    """Loads trade data."""
    file_path = os.path.join(config_dir, "trades.json")
    return load_json_data(file_path)

def get_market_data(config_dir: str = "config"):
    """Loads market data."""
    file_path = os.path.join(config_dir, "market_data.json")
    return load_json_data(file_path)

def get_simulation_params(config_dir: str = "config"):
    """Loads simulation parameters."""
    file_path = os.path.join(config_dir, "simulation_params.json")
    return load_json_data(file_path)

class ConfigManager:
    """A simple class to manage configuration loading."""
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.trades = None
        self.market_data = None
        self.sim_params = None
        print(f"ConfigManager initialized for directory: {config_dir}")

    def load_all(self):
        """Loads all configuration files."""
        print("ConfigManager: Loading all configurations...")
        self.trades = get_trades(self.config_dir)
        self.market_data = get_market_data(self.config_dir)
        self.sim_params = get_simulation_params(self.config_dir)
        print("ConfigManager: All configurations loaded.")
        return self

if __name__ == '__main__':
    # Example Usage
    print("Testing data_management.loader...")
    cfg_manager = ConfigManager(config_dir="../config") # Adjust path if running directly
    cfg_manager.load_all()
    print("\nTrades:", cfg_manager.trades)
    print("\nMarket Data:", cfg_manager.market_data)
    print("\nSimulation Params:", cfg_manager.sim_params) 