"""
Visualizations Module
---------------------
Generates institutional-grade financial charts for portfolio risk and performance analysis.
Saves generated plots as high-resolution PNG images in the 'output' directory.

Charts Created:
1. Normalized Price Trend Chart
2. Cumulative Returns Chart (Portfolio vs. Individual Assets)
3. Rolling 30-Day Annualized Volatility Chart
4. Correlation Matrix Heatmap
5. Drawdown Over Time Chart ("Underwater Chart")

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np

# Apply dark/modern quantitative styling
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['grid.color'] = '#2A2E39'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.5


def ensure_output_dir(output_dir: str = "output"):
    """Create output directory if it does not exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def plot_price_trend(price_df: pd.DataFrame, output_dir: str = "output"):
    """
    Plot normalized price movement starting at 100 base index.

    Intuition:
    ----------
    Since stock prices differ dramatically in absolute value (e.g., $180 vs $2500),
    re-indexing all prices to 100 on Day 0 allows direct comparison of historical growth trajectories.
    """
    ensure_output_dir(output_dir)
    normalized_prices = price_df / price_df.iloc[0] * 100

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    for col in normalized_prices.columns:
        ax.plot(normalized_prices.index, normalized_prices[col], label=col, linewidth=2.0)

    ax.set_title("Normalized Price Performance (Base = 100)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Re-indexed Value ($)", fontsize=11)
    ax.legend(loc="upper left", frameon=True, facecolor='#1E222D', edgecolor='#444444')
    ax.grid(True)
    fig.tight_layout()

    save_path = os.path.join(output_dir, "price_trend.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Price trend chart exported to '{save_path}'")


def plot_cumulative_returns(
    daily_returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    output_dir: str = "output"
):
    """
    Plot cumulative returns for individual assets vs weighted Portfolio.
    """
    ensure_output_dir(output_dir)
    cum_returns = (1 + daily_returns).cumprod() - 1
    cum_port_returns = (1 + portfolio_returns).cumprod() - 1

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    # Plot individual stocks with thinner/translucent lines
    for col in cum_returns.columns:
        ax.plot(cum_returns.index, cum_returns[col], label=col, linewidth=1.5, alpha=0.7)

    # Highlight Portfolio with a prominent gold/yellow line
    ax.plot(cum_port_returns.index, cum_port_returns, label="PORTFOLIO", color="#FFD700", linewidth=3.0)

    ax.set_title("Cumulative Growth: Portfolio vs. Individual Stocks", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Cumulative Return", fontsize=11)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.legend(loc="upper left", frameon=True, facecolor='#1E222D', edgecolor='#444444')
    ax.grid(True)
    fig.tight_layout()

    save_path = os.path.join(output_dir, "cumulative_returns.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Cumulative returns chart exported to '{save_path}'")


def plot_rolling_volatility(
    daily_returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    window: int = 30,
    output_dir: str = "output"
):
    """
    Plot 30-day rolling annualized volatility.

    Intuition:
    ----------
    Volatility is not constant over time (volatility clustering).
    Rolling volatility highlights market regime changes and periods of extreme stress.
    Rolling Vol = Std_Dev(30-day window) * sqrt(252)
    """
    ensure_output_dir(output_dir)
    rolling_vol = daily_returns.rolling(window=window).std() * np.sqrt(252)
    rolling_port_vol = portfolio_returns.rolling(window=window).std() * np.sqrt(252)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    for col in rolling_vol.columns:
        ax.plot(rolling_vol.index, rolling_vol[col], label=col, linewidth=1.5, alpha=0.6)

    ax.plot(rolling_port_vol.index, rolling_port_vol, label="PORTFOLIO", color="#FFD700", linewidth=2.8)

    ax.set_title(f"Rolling {window}-Day Annualized Volatility", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Annualized Standard Deviation", fontsize=11)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.legend(loc="upper left", frameon=True, facecolor='#1E222D', edgecolor='#444444')
    ax.grid(True)
    fig.tight_layout()

    save_path = os.path.join(output_dir, "rolling_volatility.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Rolling volatility chart exported to '{save_path}'")


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, output_dir: str = "output"):
    """
    Plot annotated heatmap of daily return correlations.
    """
    ensure_output_dir(output_dir)

    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1.0,
        vmax=1.0,
        square=True,
        linewidths=1.0,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title("Stock Daily Returns Correlation Matrix", fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()

    save_path = os.path.join(output_dir, "correlation_heatmap.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Correlation heatmap exported to '{save_path}'")


def plot_drawdown_chart(
    daily_returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    output_dir: str = "output"
):
    """
    Plot Drawdown trajectory over time ("Underwater Chart").

    Intuition:
    ----------
    Visualizes percentage distance from historical all-time peak at every date.
    Highlights drawdown duration (time to recovery) and maximum portfolio stress.
    """
    ensure_output_dir(output_dir)

    # Compute wealth indices and drawdowns
    wealth_index = (1 + daily_returns).cumprod()
    peaks = wealth_index.cummax()
    drawdowns = (wealth_index - peaks) / peaks

    port_wealth = (1 + portfolio_returns).cumprod()
    port_peak = port_wealth.cummax()
    port_drawdown = (port_wealth - port_peak) / port_peak

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    # Plot asset drawdowns
    for col in drawdowns.columns:
        ax.plot(drawdowns.index, drawdowns[col], label=col, linewidth=1.2, alpha=0.5)

    # Fill portfolio drawdown area
    ax.plot(port_drawdown.index, port_drawdown, label="PORTFOLIO", color="#FF5252", linewidth=2.5)
    ax.fill_between(port_drawdown.index, port_drawdown, 0, color="#FF5252", alpha=0.25)

    ax.set_title("Drawdown Trajectory Over Time (Underwater Chart)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Drawdown Percentage", fontsize=11)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.legend(loc="lower left", frameon=True, facecolor='#1E222D', edgecolor='#444444')
    ax.grid(True)
    fig.tight_layout()

    save_path = os.path.join(output_dir, "drawdown_chart.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Drawdown chart exported to '{save_path}'")


def generate_all_plots(
    price_df: pd.DataFrame,
    daily_returns: pd.DataFrame,
    portfolio_returns: pd.Series,
    corr_matrix: pd.DataFrame,
    output_dir: str = "output"
):
    """
    Master generator function to produce all 5 charts.
    """
    print("\n[INFO] Generating analytical charts...")
    plot_price_trend(price_df, output_dir=output_dir)
    plot_cumulative_returns(daily_returns, portfolio_returns, output_dir=output_dir)
    plot_rolling_volatility(daily_returns, portfolio_returns, window=30, output_dir=output_dir)
    plot_correlation_heatmap(corr_matrix, output_dir=output_dir)
    plot_drawdown_chart(daily_returns, portfolio_returns, output_dir=output_dir)
    print(f"[SUCCESS] All 5 charts generated and saved in directory '{output_dir}/'.")
