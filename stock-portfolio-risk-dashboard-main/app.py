"""
Stock Portfolio Risk Dashboard - Streamlit Web Application
----------------------------------------------------------
A quantitative financial dashboard built with Streamlit and Plotly.
Designed for quantitative analysis, portfolio risk management, and interview preparation.

Run locally:
  streamlit run app.py

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import streamlit as st
import pandas as pd
import numpy as np

from data_fetcher import fetch_stock_data
from metrics import compute_all_metrics
from web_visualizations import (
    create_price_trend_fig,
    create_cumulative_returns_fig,
    create_rolling_volatility_fig,
    create_correlation_heatmap_fig,
    create_drawdown_fig
)

# Set Streamlit Page Config
st.set_page_config(
    page_title="Stock Risk & Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Financial Dark Theme Styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0E1117;
        color: #E0E3EB;
    }
    
    /* Header Banner */
    .main-header {
        background: linear-gradient(135deg, #1E222D 0%, #131722 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #2A2E39;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .main-header h1 {
        color: #3B82F6;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0 0 8px 0;
    }
    
    .main-header p {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin: 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1E222D;
        border: 1px solid #2A2E39;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F3F4F6;
    }
    .metric-value.positive { color: #10B981; }
    .metric-value.negative { color: #EF4444; }
    .metric-value.highlight { color: #F59E0B; }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("## ⚙️ Portfolio Settings")

# 1. Ticker Selection
default_tickers = "AAPL, GOOGL, TSLA, RELIANCE.NS"
user_tickers_input = st.sidebar.text_input(
    "Stock Tickers (comma separated):",
    value=default_tickers,
    help="Enter stock symbols from US (e.g. AAPL, MSFT, NVDA) or India NSE (e.g. RELIANCE.NS, TCS.NS)"
)
tickers = [t.strip().upper() for t in user_tickers_input.split(",") if t.strip()]

# Preset Quick Selector
st.sidebar.markdown("**Quick Presets:**")
col_p1, col_p2 = st.sidebar.columns(2)
if col_p1.button("🇺🇸 US Big Tech"):
    tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]
if col_p2.button("🇮🇳 India Bluechips"):
    tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

# 2. Time Horizon
period = st.sidebar.selectbox(
    "Time Horizon:",
    options=["1y", "2y", "5y", "max"],
    index=1,
    help="Historical price timeframe for analysis"
)

# 3. Risk-Free Rate
rf_input = st.sidebar.slider(
    "Risk-Free Rate (% per year):",
    min_value=0.0,
    max_value=10.0,
    value=5.0,
    step=0.5,
    help="Benchmark return (e.g. 4.0% for US Treasuries, 6.5% for Indian Repo Rate)"
) / 100.0

# 4. Weighting Scheme
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚖️ Asset Allocation")
weighting_mode = st.sidebar.radio(
    "Portfolio Weighting:",
    options=["Equal-Weighted (1/N)", "Custom Weights"]
)

custom_weights = None
if weighting_mode == "Custom Weights" and len(tickers) > 0:
    st.sidebar.markdown("**Set Weight Per Stock:**")
    raw_weights = []
    default_weight = float(round(1.0 / len(tickers), 2))
    for t in tickers:
        w = st.sidebar.number_input(f"Weight for {t}:", min_value=0.0, max_value=1.0, value=default_weight, step=0.05)
        raw_weights.append(w)
    
    total_w = sum(raw_weights)
    if total_w > 0:
        custom_weights = [w / total_w for w in raw_weights]
        if not np.isclose(total_w, 1.0):
            st.sidebar.caption(f"ℹ️ Weights sum to {total_w:.2f}. Auto-normalized to sum to 100%.")


# --- MAIN HEADER ---
st.markdown("""
<div class="main-header">
    <h1>📈 Stock Portfolio Risk & Performance Dashboard</h1>
    <p>Quantitative analysis, risk-adjusted returns, volatility scaling, and correlation matrix visualization.</p>
</div>
""", unsafe_allow_html=True)


# --- DATA FETCHING & PROCESSING ---
if not tickers:
    st.warning("Please enter at least one stock ticker in the sidebar.")
    st.stop()

with st.spinner(f"Fetching historical price data for {', '.join(tickers)}..."):
    try:
        price_df = fetch_stock_data(tickers, period=period)
        summary_df, daily_returns, portfolio_returns, corr_matrix = compute_all_metrics(
            price_df, weights=custom_weights, risk_free_rate=rf_input
        )
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()


# --- EXECUTIVE METRIC CARDS ---
st.markdown("### 📊 Portfolio Executive Summary")
col1, col2, col3, col4, col5 = st.columns(5)

port_metrics = summary_df.loc["Portfolio"]

def get_class(val_str, is_drawdown=False):
    try:
        val = float(val_str.replace('%', '').replace('$', ''))
        if is_drawdown:
            return "negative" if val < -25 else "highlight"
        return "positive" if val > 0 else "negative"
    except:
        return ""

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Return</div>
        <div class="metric-value {get_class(port_metrics['Total Return'])}">{port_metrics['Total Return']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annual Return (CAGR)</div>
        <div class="metric-value {get_class(port_metrics['Annualized Return (CAGR)'])}">{port_metrics['Annualized Return (CAGR)']}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annual Volatility</div>
        <div class="metric-value highlight">{port_metrics['Annualized Volatility']}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    sharpe_val = float(port_metrics['Sharpe Ratio'])
    sharpe_class = "positive" if sharpe_val >= 1.0 else ("highlight" if sharpe_val > 0 else "negative")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Sharpe Ratio</div>
        <div class="metric-value {sharpe_class}">{port_metrics['Sharpe Ratio']}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Max Drawdown</div>
        <div class="metric-value negative">{port_metrics['Max Drawdown']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Growth & Performance",
    "📉 Volatility & Drawdown",
    "🔗 Correlation & Diversification",
    "📋 Summary Metrics Table"
])

with tab1:
    col_t1_a, col_t1_b = st.columns(2)
    with col_t1_a:
        fig_trend = create_price_trend_fig(price_df)
        st.plotly_chart(fig_trend, use_container_width=True)
    with col_t1_b:
        fig_cum = create_cumulative_returns_fig(daily_returns, portfolio_returns)
        st.plotly_chart(fig_cum, use_container_width=True)

with tab2:
    col_t2_a, col_t2_b = st.columns(2)
    with col_t2_a:
        fig_vol = create_rolling_volatility_fig(daily_returns, portfolio_returns, window=30)
        st.plotly_chart(fig_vol, use_container_width=True)
    with col_t2_b:
        fig_dd = create_drawdown_fig(daily_returns, portfolio_returns)
        st.plotly_chart(fig_dd, use_container_width=True)

with tab3:
    col_t3_a, col_t3_b = st.columns([1.2, 0.8])
    with col_t3_a:
        fig_corr = create_correlation_heatmap_fig(corr_matrix)
        st.plotly_chart(fig_corr, use_container_width=True)
    with col_t3_b:
        st.markdown("#### Diversification Takeaways")
        st.info("""
        **Modern Portfolio Theory (MPT)**:
        - Combining assets with low or negative daily return correlation ($\rho < 0.30$) reduces overall portfolio variance without reducing expected return.
        - Notice how combining cross-market assets (e.g. US Tech + Indian Bluechips) lowers total portfolio volatility below the average individual asset volatility.
        """)
        st.dataframe(corr_matrix.round(3), use_container_width=True)

with tab4:
    st.markdown("### 📋 Complete Portfolio & Asset Metrics")
    st.dataframe(summary_df, use_container_width=True)
    
    csv_data = summary_df.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Summary Report (CSV)",
        data=csv_data,
        file_name="portfolio_risk_metrics.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Built with Python, Streamlit, Plotly, and yfinance | B.Tech CSE Portfolio Candidate Project for Finance & Quant Analyst Roles")
