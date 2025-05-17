"""
Market Data Processor for Risk Modeling
Provides utilities for loading, cleaning, and transforming market data for risk models.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional, Tuple
import os
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MarketDataProcessor')

class MarketDataProcessor:
    """
    Processes market data for risk model inputs.
    
    Handles data loading, cleaning, transformation, and feature engineering
    for financial time series data used in risk models.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data processor.
        
        Args:
            data_path: Base directory for market data files (optional)
        """
        self.data_path = data_path
        self.raw_data = {}
        self.processed_data = {}
        
    def load_price_data(self, symbols: List[str], 
                       start_date: datetime, 
                       end_date: datetime,
                       source: str = 'csv') -> Dict[str, pd.DataFrame]:
        """
        Load price data for a list of symbols.
        
        Args:
            symbols: List of ticker symbols to load
            start_date: Start date for data range
            end_date: End date for data range
            source: Data source ('csv', 'api', or 'database')
            
        Returns:
            Dictionary mapping symbols to their price DataFrames
        """
        logger.info(f"Loading price data for {len(symbols)} symbols")
        
        result = {}
        
        for symbol in symbols:
            try:
                if source == 'csv':
                    if not self.data_path:
                        raise ValueError("data_path must be set for CSV source")
                    
                    # Load from CSV
                    file_path = os.path.join(self.data_path, f"{symbol}.csv")
                    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    
                    # Filter by date range
                    df = df[(df.index >= start_date) & (df.index <= end_date)]
                    
                elif source == 'api':
                    # This would connect to a market data API
                    logger.warning("API source not implemented yet")
                    continue
                    
                elif source == 'database':
                    # This would query a database
                    logger.warning("Database source not implemented yet")
                    continue
                    
                else:
                    raise ValueError(f"Unknown source: {source}")
                
                # Store the data
                result[symbol] = df
                self.raw_data[symbol] = df
                logger.debug(f"Loaded {len(df)} rows for {symbol}")
                
            except Exception as e:
                logger.error(f"Error loading data for {symbol}: {str(e)}")
                
        return result
        
    def calculate_returns(self, method: str = 'log') -> Dict[str, pd.DataFrame]:
        """
        Calculate returns from price data.
        
        Args:
            method: Return calculation method ('simple' or 'log')
            
        Returns:
            Dictionary mapping symbols to their returns DataFrames
        """
        if not self.raw_data:
            raise ValueError("No raw data loaded. Call load_price_data first.")
            
        logger.info(f"Calculating {method} returns for {len(self.raw_data)} symbols")
        
        returns = {}
        
        for symbol, df in self.raw_data.items():
            try:
                prices = df['close'] if 'close' in df.columns else df.iloc[:, 0]
                
                if method == 'simple':
                    # Simple returns: (P_t / P_{t-1}) - 1
                    ret = prices.pct_change().dropna()
                    
                elif method == 'log':
                    # Log returns: ln(P_t / P_{t-1})
                    ret = np.log(prices / prices.shift(1)).dropna()
                    
                else:
                    raise ValueError(f"Unknown return method: {method}")
                
                returns_df = pd.DataFrame({
                    'return': ret
                }, index=ret.index)
                
                returns[symbol] = returns_df
                logger.debug(f"Calculated {len(returns_df)} returns for {symbol}")
                
            except Exception as e:
                logger.error(f"Error calculating returns for {symbol}: {str(e)}")
        
        self.processed_data['returns'] = returns
        return returns
    
    def clean_data(self, handle_outliers: bool = True, 
                  handle_missing: str = 'ffill') -> Dict[str, pd.DataFrame]:
        """
        Clean the loaded data by handling outliers and missing values.
        
        Args:
            handle_outliers: Whether to remove outliers
            handle_missing: Method for handling missing values ('ffill', 'bfill', 'drop', 'interpolate')
            
        Returns:
            Dictionary of cleaned DataFrames
        """
        if not self.raw_data:
            raise ValueError("No raw data loaded. Call load_price_data first.")
            
        logger.info(f"Cleaning data for {len(self.raw_data)} symbols")
        
        cleaned_data = {}
        
        for symbol, df in self.raw_data.items():
            try:
                # Create a copy to avoid modifying the original
                cleaned_df = df.copy()
                
                # Handle missing values
                if handle_missing == 'ffill':
                    cleaned_df = cleaned_df.ffill()  # Forward fill
                elif handle_missing == 'bfill':
                    cleaned_df = cleaned_df.bfill()  # Backward fill
                elif handle_missing == 'drop':
                    cleaned_df = cleaned_df.dropna()  # Drop rows with NaN
                elif handle_missing == 'interpolate':
                    cleaned_df = cleaned_df.interpolate()  # Interpolate missing values
                
                # Handle outliers using Z-score method
                if handle_outliers:
                    for col in cleaned_df.select_dtypes(include=[np.number]).columns:
                        # Calculate Z-scores
                        z_scores = np.abs((cleaned_df[col] - cleaned_df[col].mean()) / cleaned_df[col].std())
                        
                        # Mark outliers (Z-score > 3) as NaN
                        cleaned_df.loc[z_scores > 3, col] = np.nan
                        
                        # Fill the new NaNs using the specified method
                        if handle_missing == 'ffill':
                            cleaned_df[col] = cleaned_df[col].ffill().bfill()  # Ensure no NaNs remain
                        elif handle_missing == 'bfill':
                            cleaned_df[col] = cleaned_df[col].bfill().ffill()
                        elif handle_missing == 'interpolate':
                            cleaned_df[col] = cleaned_df[col].interpolate().ffill().bfill()
                
                cleaned_data[symbol] = cleaned_df
                logger.debug(f"Cleaned data for {symbol}")
                
            except Exception as e:
                logger.error(f"Error cleaning data for {symbol}: {str(e)}")
                cleaned_data[symbol] = df  # Use original if cleaning fails
        
        self.processed_data['cleaned'] = cleaned_data
        return cleaned_data
    
    def calculate_volatility(self, window: int = 30, 
                            method: str = 'rolling',
                            annualize: bool = True) -> Dict[str, pd.Series]:
        """
        Calculate volatility for each symbol.
        
        Args:
            window: Window size for rolling calculations
            method: Volatility calculation method ('rolling', 'ewma', or 'garch')
            annualize: Whether to annualize the volatility
            
        Returns:
            Dictionary mapping symbols to their volatility Series
        """
        # Ensure returns are calculated
        if 'returns' not in self.processed_data:
            logger.info("Returns not found, calculating them first")
            self.calculate_returns()
        
        returns = self.processed_data['returns']
        volatilities = {}
        
        for symbol, df in returns.items():
            try:
                if method == 'rolling':
                    # Rolling standard deviation
                    vol = df['return'].rolling(window=window).std()
                    
                elif method == 'ewma':
                    # Exponentially weighted moving average
                    vol = df['return'].ewm(span=window).std()
                    
                elif method == 'garch':
                    logger.warning("GARCH method not implemented, using rolling instead")
                    vol = df['return'].rolling(window=window).std()
                    
                else:
                    raise ValueError(f"Unknown volatility method: {method}")
                
                # Annualize if requested (assuming daily data with 252 trading days)
                if annualize:
                    vol = vol * np.sqrt(252)
                
                volatilities[symbol] = vol
                logger.debug(f"Calculated volatility for {symbol}")
                
            except Exception as e:
                logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
        
        self.processed_data['volatility'] = volatilities
        return volatilities
    
    def prepare_var_model_inputs(self, symbols: List[str], 
                               lookback_period: int = 252) -> Dict[str, np.ndarray]:
        """
        Prepare inputs specific to VaR models.
        
        Args:
            symbols: Symbols to include
            lookback_period: Historical period length in trading days
            
        Returns:
            Dictionary with prepared inputs for VaR calculation
        """
        # Ensure returns and volatility are calculated
        if 'returns' not in self.processed_data:
            self.calculate_returns()
        
        if 'volatility' not in self.processed_data:
            self.calculate_volatility()
        
        returns = self.processed_data['returns']
        volatilities = self.processed_data['volatility']
        
        var_inputs = {}
        
        # Filter symbols
        selected_returns = {s: returns[s] for s in symbols if s in returns}
        
        if not selected_returns:
            raise ValueError(f"None of the requested symbols {symbols} found in processed data")
        
        # For each symbol, get the most recent returns for the lookback period
        for symbol, df in selected_returns.items():
            recent_returns = df['return'].iloc[-lookback_period:].values
            var_inputs[symbol] = recent_returns
        
        # If we have multiple symbols, also calculate correlation matrix
        if len(symbols) > 1:
            # Create DataFrame with returns columns for all symbols
            combined_returns = pd.DataFrame({
                s: df['return'] for s, df in selected_returns.items()
            })
            
            # Calculate correlation matrix using the same lookback period
            correlation_matrix = combined_returns.iloc[-lookback_period:].corr().values
            var_inputs['correlation_matrix'] = correlation_matrix
        
        logger.info(f"Prepared VaR inputs for {len(var_inputs)} symbols")
        return var_inputs

# Example usage
def run_example():
    """Run an example of the MarketDataProcessor with synthetic data."""
    # Create temporary data files for the example
    data_dir = "temp_market_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Create synthetic price data for two symbols
    dates = pd.date_range(start='2020-01-01', end='2020-12-31')
    
    # Symbol 1: Upward trend with noise
    np.random.seed(42)
    prices1 = 100 + np.cumsum(np.random.normal(0.0005, 0.01, len(dates)))
    df1 = pd.DataFrame({
        'open': prices1 * 0.99,
        'high': prices1 * 1.01,
        'low': prices1 * 0.98,
        'close': prices1,
        'volume': np.random.randint(1000, 100000, len(dates))
    }, index=dates)
    
    # Symbol 2: Downward trend with noise
    prices2 = 50 - np.cumsum(np.random.normal(0.0002, 0.008, len(dates)))
    prices2 = np.maximum(prices2, 20)  # Ensure no negative prices
    df2 = pd.DataFrame({
        'open': prices2 * 0.99,
        'high': prices2 * 1.01,
        'low': prices2 * 0.98,
        'close': prices2,
        'volume': np.random.randint(500, 50000, len(dates))
    }, index=dates)
    
    # Save to CSV
    df1.to_csv(os.path.join(data_dir, "SYMBOL1.csv"))
    df2.to_csv(os.path.join(data_dir, "SYMBOL2.csv"))
    
    # Create and use the processor
    processor = MarketDataProcessor(data_path=data_dir)
    
    # Load data
    start_date = datetime(2020, 3, 1)
    end_date = datetime(2020, 9, 30)
    symbols = ["SYMBOL1", "SYMBOL2"]
    
    price_data = processor.load_price_data(symbols, start_date, end_date)
    
    # Process data
    cleaned_data = processor.clean_data(handle_outliers=True)
    returns = processor.calculate_returns(method='log')
    volatility = processor.calculate_volatility(window=20, annualize=True)
    
    # Prepare VaR inputs
    var_inputs = processor.prepare_var_model_inputs(symbols, lookback_period=120)
    
    # Print some results
    print("\nData Processing Results:")
    print(f"Loaded {len(price_data)} symbols")
    
    for symbol in symbols:
        print(f"\n{symbol} Statistics:")
        print(f"  Days of data: {len(returns[symbol])}")
        print(f"  Average daily return: {returns[symbol]['return'].mean():.6f}")
        print(f"  Latest annualized volatility: {volatility[symbol].iloc[-1]:.4f}")
        print(f"  Returns for VaR calculation: {len(var_inputs[symbol])} days")
    
    if 'correlation_matrix' in var_inputs:
        print("\nCorrelation Matrix:")
        print(pd.DataFrame(
            var_inputs['correlation_matrix'], 
            index=symbols, 
            columns=symbols
        ))
    
    # Clean up temporary files
    for symbol in symbols:
        os.remove(os.path.join(data_dir, f"{symbol}.csv"))
    os.rmdir(data_dir)

if __name__ == "__main__":
    run_example() 