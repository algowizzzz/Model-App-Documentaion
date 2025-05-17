import time
import os
import numpy as np

from data_management.loader import ConfigManager
from simulation_engine.monte_carlo_simulator import MonteCarloEngine
from financial_instruments.equity_trs import EquityTRS
from pfe_calculation.pfe_computer import PFEQuantileCalculator
from pfe_calculation.exposure_aggregator import TradeAggregator
from reporting.output_writer import ResultsWriter

class PFECalculationOrchestrator:
    """
    Orchestrates the entire PFE calculation process.
    This class represents the "complex calculation" flow.
    """
    def __init__(self, config_path="config"):
        print("PFECalculationOrchestrator: Initializing...")
        self.config_manager = ConfigManager(config_dir=config_path)
        self.config_manager.load_all()

        self.sim_params = self.config_manager.sim_params
        self.market_data_map = self.config_manager.market_data # Map asset_id to its market data
        self.trades = self.config_manager.trades

        self.mc_engine = MonteCarloEngine(simulation_params=self.sim_params)
        self.pfe_calculator = PFEQuantileCalculator(quantile=self.sim_params['pfe_quantile'])
        self.trade_aggregator = TradeAggregator()
        
        sim_id = self.sim_params.get("simulation_id", "default_sim_id")
        output_dir_name = self.sim_params.get("output_directory", "pfe_results_output")
        # Ensure output directory is relative to the project root or an absolute path
        # For simplicity, let's assume it's a subdirectory of where main_pfe_runner is
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.output_writer = ResultsWriter(
            output_directory=os.path.join(project_root, output_dir_name), 
            simulation_id=sim_id
        )
        print("PFECalculationOrchestrator: Initialization complete.")

    def _calculate_time_parameters(self, trade_info: dict):
        """Helper to calculate total steps and dt for a trade."""
        maturity_years = trade_info['maturity_in_years']
        steps_per_year = trade_info['time_steps_per_year']
        total_time_steps = int(maturity_years * steps_per_year)
        dt = 1.0 / steps_per_year
        return total_time_steps, dt

    def process_single_trade(self, trade_info: dict):
        """
        Processes a single trade: simulate, value, calculate PFE.
        """
        trade_id = trade_info['trade_id']
        asset_id = trade_info['underlying_asset_id']
        print(f"\nPFECalculationOrchestrator: Processing trade {trade_id} for asset {asset_id}...")

        asset_market_data = self.market_data_map.get(asset_id)
        if not asset_market_data:
            print(f"Warning: Market data not found for asset {asset_id}. Skipping trade {trade_id}.")
            return

        total_simulation_steps, time_delta_t = self._calculate_time_parameters(trade_info)
        
        print(f"Trade {trade_id}: Simulating {total_simulation_steps} steps, dt={time_delta_t:.4f} years.")

        # 1. Simulate asset price paths
        underlying_price_paths = self.mc_engine.run_asset_simulation(
            asset_market_data=asset_market_data,
            total_time_steps=total_simulation_steps,
            time_delta=time_delta_t
        )

        # 2. Initialize TRS instrument and calculate MtM paths
        trs_instrument = EquityTRS(trade_details=trade_info)
        mtm_paths = trs_instrument.calculate_mtm(current_underlying_price_paths=underlying_price_paths)

        # 3. Calculate exposure paths
        exposure_paths = trs_instrument.calculate_exposure(mtm_paths=mtm_paths)
        
        # Ensure exposure at t=0 is zero if prices are at inception levels
        # (GBM starts at current_price, TRS values against initial_price_at_inception)
        # For this example, it's implicitly handled if current_price = initial_price_at_inception for t=0 in sim
        # and GBMProcess output starts with S0.

        # 4. Calculate PFE profile for this trade
        pfe_profile_trade = self.pfe_calculator.calculate_pfe_profile(exposure_paths=exposure_paths)
        
        # 5. Add to aggregator
        self.trade_aggregator.add_trade_pfe_profile(trade_id=trade_id, pfe_profile=pfe_profile_trade)
        print(f"PFECalculationOrchestrator: Finished processing trade {trade_id}.")


    def run_full_pfe_calculation(self):
        """
        Runs the PFE calculation for all trades.
        """
        print("\nPFECalculationOrchestrator: Starting full PFE calculation run...")
        start_time = time.time()

        if not self.trades:
            print("No trades found to process.")
            return

        for trade in self.trades:
            try:
                self.process_single_trade(trade)
            except Exception as e:
                print(f"Error processing trade {trade.get('trade_id', 'UNKNOWN')}: {e}")
                # Decide if you want to skip or halt on error
                # For testing, let's try to continue
                print(f"Skipping trade {trade.get('trade_id', 'UNKNOWN')} due to error.")


        # 6. Aggregate PFE (simple sum for this example)
        # aggregated_portfolio_pfe = self.trade_aggregator.calculate_simple_sum_pfe()
        # For now, let's keep aggregated_portfolio_pfe as None, to focus on individual vectors.
        # The user asked for "PFE term profile aggregated across trades AND individual vectors"
        # The simple sum is one way, or just report individual ones. Let's do sum.
        aggregated_portfolio_pfe = self.trade_aggregator.calculate_simple_sum_pfe()


        # 7. Write results
        individual_profiles = self.trade_aggregator.get_all_individual_pfe_profiles()
        self.output_writer.write_pfe_results(
            aggregated_pfe_profile=aggregated_portfolio_pfe,
            individual_pfe_profiles=individual_profiles
        )

        end_time = time.time()
        print(f"\nPFECalculationOrchestrator: Full PFE calculation completed in {end_time - start_time:.2f} seconds.")
        print(f"Results written to directory: {self.output_writer.output_directory}")


if __name__ == "__main__":
    print("===================================================")
    print("=== Monte Carlo PFE Calculator - Main Execution ===")
    print("===================================================")
    
    # Assuming your config folder is at the same level as main_pfe_runner.py or one level up
    # If MonteCarloPFE is the root, and main_pfe_runner.py is inside it, config is ./config
    orchestrator = PFECalculationOrchestrator(config_path="config")
    orchestrator.run_full_pfe_calculation()
    
    print("\n===================================================")
    print("===         PFE Calculation Finished          ===")
    print("===================================================") 