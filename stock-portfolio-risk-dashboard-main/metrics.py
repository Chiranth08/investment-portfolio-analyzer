"""
Financial Metrics Module
------------------------
Computes core quantitative risk and return metrics for individual stocks and custom/equal-weighted portfolios.

Includes:
- Daily & Cumulative Returns
- Portfolio Weighted Returns
- Annualized Return (CAGR)
- Annualized Volatility (Standard Deviation)
- Sharpe Ratio (Risk-Adjusted Excess Return)
- Maximum Drawdown (Underwater Peak-to-Trough Risk)
- Daily Return Correlation Matrix

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Union, Tuple, Optional

TRADING_DAYS_PER_YEAR = 252  # Standard number of active trading days in a calendar year


def calculate_daily_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily percentage simple returns for each asset.

    Financial Intuition:
    --------------------
    Simple returns r_t = (P_t - P_{t-1}) / P_{t-1} express the percentage change in asset value.
    Simple returns are additive across assets (enabling portfolio weighting: r_port = sum(w_i * r_i)),
    whereas log returns are additive over time.

    Parameters:
    -----------
    price_df : pd.DataFrame
        DataFrame of daily stock closing prices.

    Returns:
    --------
    pd.DataFrame
        DataFrame of daily simple percentage returns.
    """
    daily_returns = price_df.pct_change().dropna()
    return daily_returns


def calculate_portfolio_daily_returns(
    daily_returns: pd.DataFrame,
    weights: Optional[List[float]] = None
) -> pd.Series:
    """
    Calculate the daily return time series for a weighted asset portfolio.

    Financial Intuition:
    --------------------
    The daily return of a portfolio is the linear combination of individual asset returns:
    r_portfolio,t = sum(w_i * r_i,t)
    If no weights are passed, an Equal-Weighted (1/N) portfolio is constructed.

    Parameters:
    -----------
    daily_returns : pd.DataFrame
        DataFrame of daily asset returns.
    weights : List[float], optional
        List of portfolio weights corresponding to each column in daily_returns.
        Must sum to 1.0.

    Returns:
    --------
    pd.Series
        Daily portfolio returns series.
    """
    num_assets = daily_returns.shape[1]

    if weights is None:
        # Equal-weighted (1/N) portfolio
        weights_arr = np.ones(num_assets) / num_assets
    else:
        weights_arr = np.array(weights, dtype=float)
        if len(weights_arr) != num_assets:
            raise ValueError(f"Length of weights ({len(weights_arr)}) must match number of assets ({num_assets}).")
        if not np.isclose(weights_arr.sum(), 1.0):
            print(f"[WARNING] Weights sum to {weights_arr.sum():.4f}. Normalizing weights to sum to 1.0.")
            weights_arr = weights_arr / weights_arr.sum()

    # Dot product of asset daily returns and asset weight vector
    portfolio_series = daily_returns.dot(weights_arr)
    portfolio_series.name = "Portfolio"
    return portfolio_series


def calculate_cumulative_returns(daily_returns: Union[pd.DataFrame, pd.Series]) -> Union[pd.DataFrame, pd.Series]:
    """
    Calculate compounding cumulative returns over time.

    Financial Intuition:
    --------------------
    CumReturn_t = (1 + r_1) * (1 + r_2) * ... * (1 + r_t) - 1
    Represents the growth of $1 invested at the beginning of the period.

    Parameters:
    -----------
    daily_returns : pd.DataFrame or pd.Series
        Daily returns data.

    Returns:
    --------
    pd.DataFrame or pd.Series
        Cumulative returns time series.
    """
    cum_returns = (1 + daily_returns).cumprod() - 1
    return cum_returns


def calculate_annualized_return(
    daily_returns: Union[pd.DataFrame, pd.Series],
    trading_days: int = TRADING_DAYS_PER_YEAR
) -> Union[pd.Series, float]:
    """
    Compute Annualized Return (Compound Annual Growth Rate - CAGR).

    Financial Intuition:
    --------------------
    CAGR standardizes total return over an annualized 252-day trading timeline:
    CAGR = (1 + Total_Return)^(252 / N_days) - 1
    This enables direct performance comparison across assets with different sample durations.

    Parameters:
    -----------
    daily_returns : pd.DataFrame or pd.Series
        Daily percentage returns.
    trading_days : int, default 252
        Trading days in a year.

    Returns:
    --------
    pd.Series or float
        Annualized return percentage.
    """
    num_days = len(daily_returns)
    total_cum_return = (1 + daily_returns).prod() - 1
    annualized_return = (1 + total_cum_return) ** (trading_days / num_days) - 1
    return annualized_return


def calculate_annualized_volatility(
    daily_returns: Union[pd.DataFrame, pd.Series],
    trading_days: int = TRADING_DAYS_PER_YEAR
) -> Union[pd.Series, float]:
    """
    Compute Annualized Volatility (Standard Deviation of Daily Returns).

    Financial Intuition:
    --------------------
    Volatility measures total investment risk (dispersion of returns around mean).
    Assuming independent daily returns (random walk hypothesis):
    Annualized Volatility = Daily_Std_Dev * sqrt(252)

    Parameters:
    -----------
    daily_returns : pd.DataFrame or pd.Series
        Daily percentage returns.
    trading_days : int, default 252
        Trading days in a year.

    Returns:
    --------
    pd.Series or float
        Annualized volatility.
    """
    daily_std = daily_returns.std()
    annualized_vol = daily_std * np.sqrt(trading_days)
    return annualized_vol


def calculate_sharpe_ratio(
    annualized_return: Union[pd.Series, float],
    annualized_volatility: Union[pd.Series, float],
    risk_free_rate: float = 0.05
) -> Union[pd.Series, float]:
    """
    Compute the Sharpe Ratio (Risk-Adjusted Excess Return).

    Financial Intuition:
    --------------------
    Sharpe Ratio = (Annualized Return - Risk_Free_Rate) / Annualized Volatility
    Developed by Nobel laureate William F. Sharpe, it evaluates whether returns are due to
    smart investment decisions or taking excess risk.
    - Sharpe < 1.0: Suboptimal risk-adjusted return.
    - Sharpe >= 1.0: Good performance.
    - Sharpe >= 2.0: Exceptional performance.

    Parameters:
    -----------
    annualized_return : pd.Series or float
        Annualized return(s).
    annualized_volatility : pd.Series or float
        Annualized volatility.
    risk_free_rate : float, default 0.05 (5.0%)
        Risk-free rate benchmark (e.g. 4.0% for US Treasury yield, 6.5% for Indian Repo Rate).

    Returns:
    --------
    pd.Series or float
        Sharpe Ratio.
    """
    excess_return = annualized_return - risk_free_rate
    sharpe_ratio = excess_return / annualized_volatility
    return sharpe_ratio


def calculate_max_drawdown(daily_returns: Union[pd.DataFrame, pd.Series]) -> Union[pd.Series, float, pd.DataFrame]:
    """
    Compute Maximum Drawdown (MDD) and Drawdown Time Series.

    Financial Intuition:
    --------------------
    Maximum Drawdown measures peak-to-trough downside risk:
    Drawdown_t = (Wealth_t - Running_Peak_t) / Running_Peak_t
    Max Drawdown = Min(Drawdown_t)
    It indicates the worst possible loss an investor could have suffered by buying at the peak
    and selling at the absolute bottom.

    Parameters:
    -----------
    daily_returns : pd.DataFrame or pd.Series
        Daily percentage returns.

    Returns:
    --------
    max_drawdown : pd.Series or float
        Maximum peak-to-trough drawdown (expressed as negative value or percentage).
    drawdown_series : pd.DataFrame or pd.Series
        Time series of drawdowns for plotting.
    """
    wealth_index = (1 + daily_returns).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = (wealth_index - previous_peaks) / previous_peaks
    max_drawdowns = drawdowns.min()
    return max_drawdowns, drawdowns


def calculate_correlation_matrix(daily_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Pearson Correlation Matrix of asset daily returns.

    Financial Intuition:
    --------------------
    Correlation measures how assets move relative to each other:
    - Correlation = +1.0: Perfect positive correlation (move together).
    - Correlation =  0.0: Uncorrelated.
    - Correlation = -1.0: Perfect negative correlation (move in opposite directions).
    Portfolio diversification works best when combining assets with low or negative correlation,
    reducing total portfolio volatility without sacrificing expected returns (Markowitz Modern Portfolio Theory).

    Parameters:
    -----------
    daily_returns : pd.DataFrame
        DataFrame of asset daily returns.

    Returns:
    --------
    pd.DataFrame
        Pairwise correlation matrix.
    """
    return daily_returns.corr()


def compute_all_metrics(
    price_df: pd.DataFrame,
    weights: Optional[List[float]] = None,
    risk_free_rate: float = 0.05
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Master function to calculate comprehensive summary statistics for individual assets and portfolio.

    Returns:
    --------
    summary_df : pd.DataFrame
        Summary table with Annualized Return, Volatility, Sharpe Ratio, and Max Drawdown.
    daily_returns : pd.DataFrame
        Individual stock daily returns.
    portfolio_daily_returns : pd.Series
        Portfolio daily returns.
    correlation_matrix : pd.DataFrame
        Daily return correlation matrix.
    """
    # 1. Individual daily returns
    daily_returns = calculate_daily_returns(price_df)

    # 2. Portfolio daily returns
    portfolio_returns = calculate_portfolio_daily_returns(daily_returns, weights=weights)

    # Combine asset returns and portfolio returns into single DataFrame for unified processing
    combined_returns = daily_returns.copy()
    combined_returns["Portfolio"] = portfolio_returns

    # 3. Calculate core metrics for all
    cagr = calculate_annualized_return(combined_returns)
    volatility = calculate_annualized_volatility(combined_returns)
    sharpe = calculate_sharpe_ratio(cagr, volatility, risk_free_rate=risk_free_rate)
    max_dd, _ = calculate_max_drawdown(combined_returns)
    total_return = (1 + combined_returns).prod() - 1

    # 4. Assemble Summary DataFrame
    summary_df = pd.DataFrame({
        "Total Return": total_return,
        "Annualized Return (CAGR)": cagr,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd
    })

    # Format numeric values nicely for reporting
    summary_df_formatted = summary_df.copy()
    summary_df_formatted["Total Return"] = summary_df_formatted["Total Return"].map("{:.2%}".format)
    summary_df_formatted["Annualized Return (CAGR)"] = summary_df_formatted["Annualized Return (CAGR)"].map("{:.2%}".format)
    summary_df_formatted["Annualized Volatility"] = summary_df_formatted["Annualized Volatility"].map("{:.2%}".format)
    summary_df_formatted["Sharpe Ratio"] = summary_df_formatted["Sharpe Ratio"].map("{:.3f}".format)
    summary_df_formatted["Max Drawdown"] = summary_df_formatted["Max Drawdown"].map("{:.2%}".format)

    corr_matrix = calculate_correlation_matrix(daily_returns)

    return summary_df_formatted, daily_returns, portfolio_returns, corr_matrix
