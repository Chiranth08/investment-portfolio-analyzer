"""
Main Execution Script
---------------------
Command-Line Driver for Stock Portfolio Risk Dashboard.

Usage:
  python main.py
  python main.py --tickers AAPL GOOGL TSLA RELIANCE.NS --period 2y --rf 0.05
  python main.py --tickers AAPL GOOGL TSLA --weights 0.5 0.3 0.2 --rf 0.04

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import argparse
import sys
import io

# Reconfigure stdout for UTF-8 encoding on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
from tabulate import tabulate

from data_fetcher import fetch_stock_data
from metrics import compute_all_metrics
from visualizations import generate_all_plots


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stock Portfolio Risk & Performance Dashboard (Goldman Sachs / Quant Interview Project)"
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["AAPL", "GOOGL", "TSLA", "RELIANCE.NS"],
        help="List of stock tickers (e.g. AAPL GOOGL TSLA RELIANCE.NS)"
    )
    parser.add_argument(
        "--weights",
        nargs="+",
        type=float,
        default=None,
        help="Optional portfolio weights (e.g. 0.4 0.3 0.2 0.1). Must sum to 1.0."
    )
    parser.add_argument(
        "--period",
        type=str,
        default="2y",
        help="Data timeframe (e.g. 1y, 2y, 5y, max). Default is 2y."
    )
    parser.add_argument(
        "--rf",
        type=float,
        default=0.05,
        help="Annual Risk-Free Rate (e.g. 0.04 for US 4%%, 0.065 for India 6.5%%). Default is 0.05 (5%%)."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save output PNG charts. Default is 'output'."
    )
    return parser.parse_args()


def print_banner():
    banner = """
===================================================================================
               STOCK PORTFOLIO RISK & PERFORMANCE DASHBOARD
   Quantitative Risk Analysis | Portfolio Optimization | Financial Analytics
===================================================================================
"""
    print(banner)


def main():
    print_banner()
    args = parse_args()

    tickers = args.tickers
    weights = args.weights
    period = args.period
    rf_rate = args.rf
    output_dir = args.output_dir

    print(f"[CONFIG] Tickers           : {', '.join(tickers)}")
    print(f"[CONFIG] Time Horizon      : {period}")
    print(f"[CONFIG] Risk-Free Rate    : {rf_rate:.2%}")
    if weights:
        print(f"[CONFIG] Custom Weights    : {weights}")
    else:
        print(f"[CONFIG] Portfolio Weighting: Equal-Weighted (1/N)")
    print("=" * 83 + "\n")

    try:
        # Step 1: Fetch Price Data
        prices = fetch_stock_data(tickers, period=period)

        # Step 2: Compute Quantitative Metrics
        summary_df, daily_returns, portfolio_returns, corr_matrix = compute_all_metrics(
            prices, weights=weights, risk_free_rate=rf_rate
        )

        # Step 3: Print Clean Summary Table
        print("\n" + "=" * 83)
        print("                        PORTFOLIO & ASSET METRICS SUMMARY")
        print("=" * 83)
        print(tabulate(summary_df, headers="keys", tablefmt="grid"))

        print("\n" + "=" * 83)
        print("                      DAILY RETURNS CORRELATION MATRIX")
        print("=" * 83)
        print(tabulate(corr_matrix.round(3), headers="keys", tablefmt="grid"))

        # Step 4: Generate & Save Charts
        generate_all_plots(
            prices,
            daily_returns,
            portfolio_returns,
            corr_matrix,
            output_dir=output_dir
        )

        print("\n" + "=" * 83)
        print("                        FINANCIAL INSIGHTS & TAKEAWAYS")
        print("=" * 83)
        port_cagr = summary_df.loc["Portfolio", "Annualized Return (CAGR)"]
        port_vol = summary_df.loc["Portfolio", "Annualized Volatility"]
        port_sharpe = summary_df.loc["Portfolio", "Sharpe Ratio"]
        port_mdd = summary_df.loc["Portfolio", "Max Drawdown"]

        print(f"• Portfolio Annualized Return (CAGR) : {port_cagr}")
        print(f"• Portfolio Annualized Volatility    : {port_vol}")
        print(f"• Portfolio Sharpe Ratio (Rf={rf_rate:.1%})  : {port_sharpe}")
        print(f"• Portfolio Maximum Drawdown         : {port_mdd}")
        print("\n[NOTE] Review 'output/' folder for high-resolution PNG analytical charts.")
        print("[SUCCESS] Dashboard execution completed successfully.\n")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during dashboard execution: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
