import numpy as np

class PFEQuantileCalculator:
    """
    Calculates Potential Future Exposure (PFE) at a given quantile.
    """
    def __init__(self, quantile: float):
        if not (0 < quantile < 1):
            raise ValueError("Quantile must be between 0 and 1 (exclusive).")
        self.quantile = quantile
        print(f"PFEQuantileCalculator initialized for quantile: {self.quantile}")

    def calculate_pfe_profile(self, exposure_paths: np.ndarray):
        """
        Calculates the PFE profile from exposure paths.
        PFE at each time step is the specified quantile of positive exposures across paths.

        Args:
            exposure_paths (np.ndarray): Array of exposure values.
                                         Shape: (num_time_steps + 1, num_paths)
                                         Assumes exposure_paths[0,:] is exposure at t=0 (usually 0).

        Returns:
            np.ndarray: PFE profile (a vector of PFE values over time).
                        Shape: (num_time_steps + 1,)
        """
        if exposure_paths.ndim != 2:
            raise ValueError("exposure_paths must be a 2D array (time_steps, num_paths).")
        
        # PFE is calculated at each future time step
        # np.percentile calculates along axis, so axis=1 means across paths for each time step
        pfe_profile = np.percentile(exposure_paths, self.quantile * 100, axis=1)
        
        # Ensure PFE is non-negative (though percentile of non-negative exposures should be non-negative)
        pfe_profile = np.maximum(0, pfe_profile) 
        
        print(f"PFEQuantileCalculator: PFE profile calculated.")
        return pfe_profile

if __name__ == '__main__':
    print("Testing pfe_calculation.pfe_computer...")
    # Example exposure paths: (time_steps+1, num_paths)
    # rows = time (t0, t1, t2), cols = paths
    exposures_test = np.array([
        [0,   0,   0,   0,   0  ],  # t=0, all exposures 0
        [10,  0,   20,  5,   15 ],  # t=1
        [25,  10,  0,   18,  30 ]   # t=2
    ])
    
    calculator_95 = PFEQuantileCalculator(quantile=0.95)
    pfe_95 = calculator_95.calculate_pfe_profile(exposures_test)
    print("\nPFE (95th percentile) Profile:\n", pfe_95)
    
    calculator_50 = PFEQuantileCalculator(quantile=0.50) # Median exposure
    pfe_50 = calculator_50.calculate_pfe_profile(exposures_test)
    print("\nPFE (50th percentile) Profile:\n", pfe_50)

    # Test with all zero exposures
    zero_exposures = np.zeros((3,5))
    pfe_zero = calculator_95.calculate_pfe_profile(zero_exposures)
    print("\nPFE for zero exposures:\n", pfe_zero) 