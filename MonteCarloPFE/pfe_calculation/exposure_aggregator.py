import numpy as np

class TradeAggregator:
    """
    Aggregates results across multiple trades.
    For this example, it will mainly collect PFE profiles.
    More complex aggregation (like netting) is out of scope for this 'bare-minimum' example.
    """
    def __init__(self):
        self.all_trade_pfe_profiles = {}
        self.aggregated_pfe_profile = None # Placeholder for more complex aggregation
        print("TradeAggregator initialized.")

    def add_trade_pfe_profile(self, trade_id: str, pfe_profile: np.ndarray):
        """
        Stores the PFE profile for a single trade.
        """
        if trade_id in self.all_trade_pfe_profiles:
            print(f"Warning: Overwriting PFE profile for trade_id {trade_id}")
        self.all_trade_pfe_profiles[trade_id] = pfe_profile
        print(f"TradeAggregator: Added PFE profile for trade {trade_id}")

    def get_all_individual_pfe_profiles(self):
        """Returns a dictionary of all stored PFE profiles by trade_id."""
        return self.all_trade_pfe_profiles

    def calculate_simple_sum_pfe(self):
        """
        A very basic aggregation: sums the PFE profiles of all trades.
        Note: This is generally NOT how portfolio PFE is calculated due to netting effects,
        but serves as a simple aggregation example. True portfolio PFE requires summing
        exposures *before* taking the percentile.
        """
        if not self.all_trade_pfe_profiles:
            print("TradeAggregator: No trade PFE profiles to aggregate.")
            return None

        profiles_list = list(self.all_trade_pfe_profiles.values())
        
        # Ensure all profiles have the same length
        first_profile_len = len(profiles_list[0])
        if not all(len(p) == first_profile_len for p in profiles_list):
            raise ValueError("Cannot sum PFE profiles of different lengths.")

        self.aggregated_pfe_profile = np.sum(np.array(profiles_list), axis=0)
        print("TradeAggregator: Calculated simple sum aggregated PFE profile.")
        return self.aggregated_pfe_profile

if __name__ == '__main__':
    print("Testing pfe_calculation.exposure_aggregator...")
    aggregator = TradeAggregator()
    
    pfe1 = np.array([0, 10, 20, 15])
    pfe2 = np.array([0, 5,  10, 12])
    
    aggregator.add_trade_pfe_profile("TradeA", pfe1)
    aggregator.add_trade_pfe_profile("TradeB", pfe2)
    
    individual_pfes = aggregator.get_all_individual_pfe_profiles()
    print("\nIndividual PFE Profiles:", individual_pfes)
    
    summed_pfe = aggregator.calculate_simple_sum_pfe()
    print("\nSimple Summed PFE Profile:", summed_pfe)

    aggregator_empty = TradeAggregator()
    print("\nSimple Summed PFE (empty):", aggregator_empty.calculate_simple_sum_pfe()) 