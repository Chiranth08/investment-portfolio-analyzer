"""
Data Fetcher Module
-------------------
Fetches daily historical price data from Yahoo Finance (yfinance) for a list of stock tickers.
Handles multi-ticker alignment, missing data handling across global exchanges (e.g., US vs NSE India),
and price extraction (Adjusted Close / Close).

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple


def fetch_stock_data(
    tickers: List[str],
    period: str = "2y",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch daily closing price data for specified tickers using yfinance.

    Financial / Quantitative Logic:
    -------------------------------
    - Adjusted Close ('Adj Close') is preferred over raw Close price because it adjusts
      for stock splits, dividends, and corporate actions, providing a true total return representation.
    - Global exchanges (e.g. NASDAQ vs NSE India) have different holiday schedules.
      When combining global tickers, missing dates arise on one exchange when another is open.
      We forward-fill (`ffill`) missing values assuming the asset value remains constant
      over non-trading days, preventing artificial zero returns.

    Parameters:
    -----------
    tickers : List[str]
        List of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'TSLA', 'RELIANCE.NS']).
    period : str, default '2y'
        Valid yfinance period string (e.g., '1y', '2y', '5y', 'max').
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format. Overrides period if provided.
    end_date : str, optional
        End date in 'YYYY-MM-DD' format. Overrides period if provided.

    Returns:
    --------
    pd.DataFrame
        DataFrame of daily closing prices where columns are ticker symbols and index is DatetimeIndex.
    """
    cleaned_tickers = [t.strip().upper() for t in tickers if t.strip()]
    if not cleaned_tickers:
        raise ValueError("No valid tickers provided.")

    print(f"[INFO] Fetching historical price data for: {', '.join(cleaned_tickers)}...")
    
    # Download data from yfinance
    if start_date and end_date:
        df = yf.download(cleaned_tickers, start=start_date, end=end_date, progress=False)
    else:
        df = yf.download(cleaned_tickers, period=period, progress=False)

    if df.empty:
        raise RuntimeError("No data returned from yfinance. Please check ticker symbols and network connection.")

    # Extract Close or Adj Close prices
    if 'Adj Close' in df.columns:
        price_df = df['Adj Close']
    elif 'Close' in df.columns:
        price_df = df['Close']
    else:
        # Single ticker case or multi-level index handling
        price_df = df

    # If single ticker was requested, yfinance returns a Series or single-column DataFrame
    if isinstance(price_df, pd.Series):
        price_df = price_df.to_frame(name=cleaned_tickers[0])
    elif len(cleaned_tickers) == 1 and isinstance(price_df, pd.DataFrame):
        if price_df.columns.nlevels > 1:
            price_df = price_df.iloc[:, 0].to_frame(name=cleaned_tickers[0])
        else:
            price_df.columns = cleaned_tickers

    # Align columns in requested ticker order
    available_cols = [col for col in cleaned_tickers if col in price_df.columns]
    if not available_cols:
        # Fallback if columns are named differently
        price_df.columns = [str(col).upper() for col in price_df.columns]
        available_cols = [col for col in cleaned_tickers if col in price_df.columns]

    price_df = price_df[available_cols]

    # Handle missing values (e.g. cross-border trading calendar mismatches)
    # 1. Forward-fill: fill holiday missing values with previous trading day's price
    # 2. Backward-fill: for initial missing values if tickers started trading at different dates
    price_df = price_df.ffill().bfill()

    # Drop any remaining unfillable NaN rows
    price_df.dropna(axis=0, how='any', inplace=True)

    print(f"[SUCCESS] Downloaded {len(price_df)} trading days of price data from {price_df.index[0].strftime('%Y-%m-%d')} to {price_df.index[-1].strftime('%Y-%m-%d')}.")
    
    return price_df


if __name__ == "__main__":
    # Test execution
    sample_tickers = ["AAPL", "GOOGL", "TSLA", "RELIANCE.NS"]
    prices = fetch_stock_data(sample_tickers, period="2y")
    print("\nSample Price Head:")
    print(prices.head())
