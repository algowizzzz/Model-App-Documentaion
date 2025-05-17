# Monte Carlo PFE Calculator for Equity TRS

This project calculates Potential Future Exposure (PFE) for a portfolio of Equity Total Return Swaps (TRS) 
using Monte Carlo simulation. The underlying equity prices are modeled using Geometric Brownian Motion (GBM).

## Project Structure

- `config/`: Contains JSON files for trade data, market data, and simulation parameters.
- `data_management/`: Modules for loading and managing input data.
- `financial_instruments/`: Modules for defining and valuing financial instruments (e.g., Equity TRS).
- `pfe_calculation/`: Modules for calculating exposures and aggregating PFE.
- `reporting/`: Modules for writing output results.
- `simulation_engine/`: Modules for the Monte Carlo simulation and underlying stochastic processes (GBM).
- `main_pfe_runner.py`: The main script to execute the PFE calculation.
- `pfe_results/`: (Will be created to store output)

## Workflow

1.  **Load Data**: Read trade details, market parameters, and simulation settings from JSON files in the `config/` directory.
2.  **Simulate Price Paths**: For each underlying asset, generate multiple price paths over time using the Geometric Brownian Motion (GBM) model.
3.  **Value Trades**: For each trade and each simulated price path, calculate the mark-to-market (MtM) value of the Equity TRS at each future time step.
4.  **Calculate Exposures**: At each time step, for each trade on each path, determine the exposure. Exposure is typically `max(0, MtM_value)` if the counterparty owes us.
5.  **Compute PFE per Trade**: For each trade, determine the PFE profile by taking a specific percentile (e.g., 95th or 99th) of the positive exposures across all simulated paths at each future time step. This gives a vector of PFE values over time for that trade.
6.  **Aggregate PFE (Optional)**: Calculate an aggregated PFE profile across all trades. This can be done in various ways (e.g., summing PFE profiles, or re-calculating PFE from summed exposures, which is more accurate but complex). For this example, we might sum individual PFE profiles or just output them separately.
7.  **Write Results**: Save the aggregated PFE term profile and the individual PFE vectors for each trade into an output directory (`pfe_results/`), typically in JSON or CSV format. 