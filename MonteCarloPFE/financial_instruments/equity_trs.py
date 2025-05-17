import numpy as np

class EquityTRS:
    """
    Represents and values an Equity Total Return Swap.
    For simplicity, assumes the funding leg (fixed or floating rate payments) is netted against
    the equity leg at each valuation date. We will focus on the change in equity value.
    The value of the TRS is (Current Equity Value - Initial Equity Value) for receiver,
    and opposite for payer.
    """
    def __init__(self, trade_details: dict):
        """
        Args:
            trade_details (dict): Contains 'notional', 'initial_price_at_inception', 'trade_type'.
        """
        self.notional = float(trade_details['notional'])
        self.initial_price = float(trade_details['initial_price_at_inception'])
        self.trade_type = trade_details['trade_type'] # 'receive_equity_return' or 'pay_equity_return'
        
        if self.trade_type not in ['receive_equity_return', 'pay_equity_return']:
            raise ValueError(f"Invalid trade_type: {self.trade_type}")
        print(f"EquityTRS instrument created for trade: Notional={self.notional}, InitialPrice={self.initial_price}, Type={self.trade_type}")

    def calculate_mtm(self, current_underlying_price_paths: np.ndarray):
        """
        Calculates the Mark-to-Market (MtM) of the TRS.
        Assumes current_underlying_price_paths is an array of prices (time_steps, num_paths).

        Args:
            current_underlying_price_paths (np.ndarray): Array of current prices of the underlying.
                                                        Shape: (num_time_steps + 1, num_paths)

        Returns:
            np.ndarray: MtM values for each path and time step.
                        Shape: (num_time_steps + 1, num_paths)
        """
        # Equity leg value change: (St / S0 - 1) * Notional
        # Or more simply: (St - S0) * (Notional / S0)
        # Let's use (St - S0) / S0 * Notional, assuming S0 is the price at trade inception.
        
        price_ratio_change = (current_underlying_price_paths - self.initial_price) / self.initial_price
        mtm_values = price_ratio_change * self.notional

        if self.trade_type == 'pay_equity_return':
            mtm_values = -mtm_values # Payer has opposite MtM to receiver

        print(f"EquityTRS: MtM calculated. Example mtm_values[0,0] if paths were non-zero: {mtm_values[0,0] if mtm_values.size > 0 else 'N/A'}")
        return mtm_values

    def calculate_exposure(self, mtm_paths: np.ndarray):
        """
        Calculates exposure from MtM paths. Exposure = max(0, MtM).
        This assumes positive MtM means the counterparty owes us.

        Args:
            mtm_paths (np.ndarray): Mark-to-Market values. Shape (num_time_steps+1, num_paths)

        Returns:
            np.ndarray: Exposure values. Shape (num_time_steps+1, num_paths)
        """
        exposures = np.maximum(0, mtm_paths)
        print(f"EquityTRS: Exposures calculated.")
        return exposures


if __name__ == '__main__':
    print("Testing financial_instruments.equity_trs...")
    trade_details_test_receiver = {
        "notional": 100000,
        "initial_price_at_inception": 100,
        "trade_type": "receive_equity_return"
    }
    trs_receiver = EquityTRS(trade_details_test_receiver)

    # Example price paths: (time_steps+1, num_paths)
    # rows = time steps (0, 1, 2), cols = paths (pathA, pathB)
    example_prices = np.array([
        [100, 100],  # Initial price at t=0
        [105, 95],   # Prices at t=1
        [110, 90]    # Prices at t=2
    ])

    mtm_receiver = trs_receiver.calculate_mtm(example_prices)
    print("\nMtM for Receiver:\n", mtm_receiver)
    exposures_receiver = trs_receiver.calculate_exposure(mtm_receiver)
    print("\nExposures for Receiver:\n", exposures_receiver)

    trade_details_test_payer = {
        "notional": 100000,
        "initial_price_at_inception": 100,
        "trade_type": "pay_equity_return"
    }
    trs_payer = EquityTRS(trade_details_test_payer)
    mtm_payer = trs_payer.calculate_mtm(example_prices)
    print("\nMtM for Payer:\n", mtm_payer)
    exposures_payer = trs_payer.calculate_exposure(mtm_payer)
    print("\nExposures for Payer:\n", exposures_payer) 