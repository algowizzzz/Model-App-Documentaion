import numpy as np

class GBMProcess:
    """
    Geometric Brownian Motion process for simulating asset prices.
    S(t+dt) = S(t) * exp((mu - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z)
    where Z is a standard normal random variable.
    """
    def __init__(self, initial_price, drift, volatility, time_delta):
        """
        Args:
            initial_price (float): S0, the starting price of the asset.
            drift (float): mu, the expected rate of return (e.g., risk-free rate - dividend yield).
            volatility (float): sigma, the volatility of the asset price.
            time_delta (float): dt, the time increment for each step (in years).
        """
        self.initial_price = float(initial_price)
        self.drift = float(drift)
        self.volatility = float(volatility)
        self.time_delta = float(time_delta)
        print(f"GBMProcess initialized: S0={self.initial_price}, mu={self.drift}, sigma={self.volatility}, dt={self.time_delta}")

    def generate_paths(self, num_steps: int, num_paths: int):
        """
        Generates multiple asset price paths.

        Args:
            num_steps (int): The number of time steps to simulate for each path.
            num_paths (int): The number of distinct paths to generate.

        Returns:
            numpy.ndarray: An array of shape (num_steps + 1, num_paths)
                           containing the simulated asset prices.
                           Includes the initial price at t=0.
        """
        if num_steps <= 0 or num_paths <= 0:
            raise ValueError("Number of steps and paths must be positive.")

        paths = np.zeros((num_steps + 1, num_paths))
        paths[0] = self.initial_price

        # Pre-calculate constants for efficiency
        drift_term = (self.drift - 0.5 * self.volatility**2) * self.time_delta
        vol_term = self.volatility * np.sqrt(self.time_delta)

        for t in range(1, num_steps + 1):
            random_shocks = np.random.standard_normal(num_paths)
            paths[t] = paths[t-1] * np.exp(drift_term + vol_term * random_shocks)
        
        print(f"GBMProcess: Generated {num_paths} paths with {num_steps} steps each.")
        return paths

if __name__ == '__main__':
    print("Testing simulation_engine.gbm_model...")
    gbm = GBMProcess(initial_price=100, drift=0.05, volatility=0.2, time_delta=1/12)
    price_paths = gbm.generate_paths(num_steps=12, num_paths=3) # 1 year, 3 paths
    print("\nGenerated Price Paths (Example):\n", price_paths) 