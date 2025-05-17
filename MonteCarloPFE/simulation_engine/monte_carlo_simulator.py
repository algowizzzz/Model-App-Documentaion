from .gbm_model import GBMProcess

class MonteCarloEngine:
    """
    Orchestrates Monte Carlo simulations for various assets.
    This is a somewhat conceptual class for this example, primarily to
    show another layer of modularity. The main logic might be in main_pfe_runner.
    """
    def __init__(self, simulation_params: dict):
        self.num_paths = simulation_params.get("num_paths", 1000)
        print(f"MonteCarloEngine initialized with {self.num_paths} paths.")

    def run_asset_simulation(self, asset_market_data: dict, total_time_steps: int, time_delta: float):
        """
        Simulates price paths for a single asset.

        Args:
            asset_market_data (dict): Market data for the specific asset.
            total_time_steps (int): Total number of simulation steps.
            time_delta (float): Time increment per step (dt).

        Returns:
            numpy.ndarray: Simulated price paths.
        """
        print(f"MonteCarloEngine: Running simulation for asset with initial price {asset_market_data['current_price']}")
        initial_price = asset_market_data['current_price']
        # For risk-neutral simulation of stock price for PFE, drift mu = r - q
        drift = asset_market_data['risk_free_rate'] - asset_market_data['dividend_yield']
        volatility = asset_market_data['volatility']
        
        gbm = GBMProcess(
            initial_price=initial_price,
            drift=drift,
            volatility=volatility,
            time_delta=time_delta
        )
        price_paths = gbm.generate_paths(num_steps=total_time_steps, num_paths=self.num_paths)
        print(f"MonteCarloEngine: Asset simulation completed.")
        return price_paths

if __name__ == '__main__':
    print("Testing simulation_engine.monte_carlo_simulator...")
    sim_params_test = {"num_paths": 5}
    market_data_test = {
        "current_price": 120,
        "risk_free_rate": 0.03,
        "dividend_yield": 0.01,
        "volatility": 0.15
    }
    engine = MonteCarloEngine(simulation_params=sim_params_test)
    paths = engine.run_asset_simulation(
        asset_market_data=market_data_test,
        total_time_steps=24, # 2 years, monthly
        time_delta=1/12
    )
    print("\nSimulated Paths (Example from MonteCarloEngine):\n", paths[:, :2]) # Print first 2 paths 