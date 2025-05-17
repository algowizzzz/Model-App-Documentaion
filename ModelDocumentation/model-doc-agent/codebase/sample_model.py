"""
Value at Risk (VaR) Model Implementation
A simplified risk model used for estimating potential losses in a portfolio.
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from typing import List, Dict, Union, Tuple, Optional

class VaRModel:
    """
    Value at Risk (VaR) Model for estimating potential financial losses.
    
    This class implements both historical simulation and parametric (variance-covariance)
    methods for calculating VaR at various confidence levels.
    """
    
    def __init__(self, confidence_level: float = 0.95, time_horizon: int = 1):
        """
        Initialize the VaR model with specified parameters.
        
        Args:
            confidence_level: Confidence level for VaR calculation (default: 0.95)
            time_horizon: Time horizon in days (default: 1)
        """
        self.confidence_level = confidence_level
        self.time_horizon = time_horizon
        self.returns_data = None
        self.model_params = {}
        
    def load_returns_data(self, returns: np.ndarray):
        """
        Load historical returns data into the model.
        
        Args:
            returns: Array of historical returns
        """
        self.returns_data = returns
        self.model_params["data_points"] = len(returns)
        self.model_params["mean_return"] = np.mean(returns)
        self.model_params["volatility"] = np.std(returns)
        
    def calculate_historical_var(self) -> float:
        """
        Calculate VaR using historical simulation method.
        
        Returns:
            Value at Risk estimate based on historical data
        """
        if self.returns_data is None:
            raise ValueError("Returns data must be loaded before calculating VaR")
            
        # Sort returns from worst to best
        sorted_returns = np.sort(self.returns_data)
        
        # Calculate the index corresponding to the confidence level
        index = int(len(sorted_returns) * (1 - self.confidence_level))
        
        # The VaR is the absolute value of the return at that index
        var = abs(sorted_returns[index]) 
        
        # Scale by square root of time for multi-day horizons
        if self.time_horizon > 1:
            var = var * np.sqrt(self.time_horizon)
            
        return var
    
    def calculate_parametric_var(self) -> float:
        """
        Calculate VaR using parametric (variance-covariance) method.
        
        Returns:
            Value at Risk estimate based on normal distribution
        """
        if self.returns_data is None:
            raise ValueError("Returns data must be loaded before calculating VaR")
            
        # Calculate mean and standard deviation
        mean = self.model_params["mean_return"]
        volatility = self.model_params["volatility"]
        
        # Calculate VaR using normal distribution quantile
        z_score = stats.norm.ppf(1 - self.confidence_level)
        var = -(mean + z_score * volatility)
        
        # Ensure VaR is positive
        var = abs(var)
        
        # Scale by square root of time for multi-day horizons
        if self.time_horizon > 1:
            var = var * np.sqrt(self.time_horizon)
            
        return var
    
    def run_monte_carlo_var(self, num_simulations: int = 10000) -> float:
        """
        Calculate VaR using Monte Carlo simulation.
        
        Args:
            num_simulations: Number of simulations to run
            
        Returns:
            Value at Risk estimate based on Monte Carlo simulation
        """
        if self.returns_data is None:
            raise ValueError("Returns data must be loaded before calculating VaR")
            
        mean = self.model_params["mean_return"]
        volatility = self.model_params["volatility"]
        
        # Generate random returns under normal distribution assumption
        simulated_returns = np.random.normal(mean, volatility, num_simulations)
        
        # Sort simulated returns
        sorted_returns = np.sort(simulated_returns)
        
        # Calculate the index corresponding to the confidence level
        index = int(num_simulations * (1 - self.confidence_level))
        
        # The VaR is the absolute value of the return at that index
        var = abs(sorted_returns[index])
        
        # Scale by square root of time for multi-day horizons
        if self.time_horizon > 1:
            var = var * np.sqrt(self.time_horizon)
            
        return var
    
    def compare_var_methods(self) -> Dict[str, float]:
        """
        Compare different VaR calculation methods.
        
        Returns:
            Dictionary with VaR values for each method
        """
        results = {
            "historical": self.calculate_historical_var(),
            "parametric": self.calculate_parametric_var(),
            "monte_carlo": self.run_monte_carlo_var()
        }
        return results
    
    def plot_var_comparison(self, save_path: Optional[str] = None):
        """
        Generate a plot comparing different VaR methods.
        
        Args:
            save_path: Path to save the plot (if None, plot is displayed)
        """
        var_values = self.compare_var_methods()
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(var_values.keys(), var_values.values())
        plt.title(f"VaR Comparison at {self.confidence_level*100}% Confidence Level")
        plt.ylabel("Value at Risk")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

# Example usage
def run_example():
    # Generate sample returns data (normally distributed for simplicity)
    np.random.seed(42)  # For reproducibility
    returns = np.random.normal(-0.001, 0.02, 1000)  # 1000 days of returns
    
    # Initialize model and calculate VaR
    var_model = VaRModel(confidence_level=0.99, time_horizon=1)
    var_model.load_returns_data(returns)
    
    # Print results
    var_results = var_model.compare_var_methods()
    print(f"99% VaR Estimates (1-day horizon):")
    for method, value in var_results.items():
        print(f"  {method.capitalize()} method: {value:.4f} (or {value*100:.2f}%)")
    
    # Plot comparison
    var_model.plot_var_comparison()

if __name__ == "__main__":
    run_example() 