"""
Web Visualizations Module (Plotly)
----------------------------------
Generates interactive, dark-themed Plotly charts for the Streamlit web dashboard.

Includes:
1. Re-indexed Price Performance Chart (Base 100)
2. Cumulative Returns Chart (Portfolio vs. Asset Constituents)
3. Rolling 30-Day Annualized Volatility Chart
4. Correlation Matrix Heatmap
5. Drawdown Trajectory Area Chart ("Underwater Chart")

Author: B.Tech CSE Portfolio Candidate
Target: Finance / Quantitative Analyst Roles
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# Dark financial theme layout configuration
DARK_LAYOUT = dict(
    paper_bgcolor='#1E222D',
    plot_bgcolor='#131722',
    font=dict(color='#E0E3EB', family='sans-serif'),
    xaxis=dict(gridcolor='#2A2E39', zerolinecolor='#2A2E39', showgrid=True),
    yaxis=dict(gridcolor='#2A2E39', zerolinecolor='#2A2E39', showgrid=True),
    margin=dict(l=45, r=30, t=55, b=75),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.22,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(0,0,0,0)"
    )
)


def create_price_trend_fig(price_df: pd.DataFrame) -> go.Figure:
    """Create interactive normalized price trend chart (Base = 100)."""
    norm_prices = price_df / price_df.iloc[0] * 100
    fig = go.Figure()

    for col in norm_prices.columns:
        fig.add_trace(go.Scatter(
            x=norm_prices.index,
            y=norm_prices[col],
            mode='lines',
            name=col,
            hovertemplate=f"<b>{col}</b><br>Date: %{{x|%Y-%m-%d}}<br>Index: %{{y:.2f}}<extra></extra>",
            line=dict(width=2)
        ))

    fig.update_layout(
        title=dict(
            text="<b>Normalized Price Performance (Base = 100)</b>",
            x=0.02,
            y=0.96,
            font=dict(size=15, color='#F3F4F6')
        ),
        yaxis_title="Re-indexed Value ($)",
        xaxis_title="Date",
        **DARK_LAYOUT
    )
    return fig


def create_cumulative_returns_fig(daily_returns: pd.DataFrame, portfolio_returns: pd.Series) -> go.Figure:
    """Create interactive cumulative returns chart."""
    cum_returns = (1 + daily_returns).cumprod() - 1
    cum_port = (1 + portfolio_returns).cumprod() - 1

    fig = go.Figure()

    # Individual constituent assets
    for col in cum_returns.columns:
        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=cum_returns[col] * 100,
            mode='lines',
            name=col,
            opacity=0.75,
            hovertemplate=f"<b>{col}</b><br>Date: %{{x|%Y-%m-%d}}<br>Cum Return: %{{y:.2f}}%<extra></extra>",
            line=dict(width=1.5)
        ))

    # PORTFOLIO trace highlighted in gold
    fig.add_trace(go.Scatter(
        x=cum_port.index,
        y=cum_port * 100,
        mode='lines',
        name='PORTFOLIO',
        hovertemplate="<b>PORTFOLIO</b><br>Date: %{x|%Y-%m-%d}<br>Cum Return: %{y:.2f}%<extra></extra>",
        line=dict(color='#FFD700', width=3.5)
    ))

    fig.update_layout(
        title=dict(
            text="<b>Cumulative Growth: Portfolio vs. Stocks</b>",
            x=0.02,
            y=0.96,
            font=dict(size=15, color='#F3F4F6')
        ),
        yaxis_title="Cumulative Return (%)",
        xaxis_title="Date",
        **DARK_LAYOUT
    )
    return fig


def create_rolling_volatility_fig(daily_returns: pd.DataFrame, portfolio_returns: pd.Series, window: int = 30) -> go.Figure:
    """Create interactive 30-day rolling annualized volatility chart."""
    rolling_vol = daily_returns.rolling(window=window).std() * np.sqrt(252) * 100
    rolling_port_vol = portfolio_returns.rolling(window=window).std() * np.sqrt(252) * 100

    fig = go.Figure()

    for col in rolling_vol.columns:
        fig.add_trace(go.Scatter(
            x=rolling_vol.index,
            y=rolling_vol[col],
            mode='lines',
            name=col,
            opacity=0.6,
            hovertemplate=f"<b>{col}</b><br>Date: %{{x|%Y-%m-%d}}<br>30D Vol: %{{y:.2f}}%<extra></extra>",
            line=dict(width=1.5)
        ))

    fig.add_trace(go.Scatter(
        x=rolling_port_vol.index,
        y=rolling_port_vol,
        mode='lines',
        name='PORTFOLIO',
        hovertemplate="<b>PORTFOLIO</b><br>Date: %{x|%Y-%m-%d}<br>30D Vol: %{y:.2f}%<extra></extra>",
        line=dict(color='#FFD700', width=3.0)
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Rolling {window}-Day Annualized Volatility</b>",
            x=0.02,
            y=0.96,
            font=dict(size=15, color='#F3F4F6')
        ),
        yaxis_title="Annualized Volatility (%)",
        xaxis_title="Date",
        **DARK_LAYOUT
    )
    return fig


def create_correlation_heatmap_fig(corr_matrix: pd.DataFrame) -> go.Figure:
    """Create interactive correlation heatmap."""
    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
        labels=dict(x="Asset", y="Asset", color="Pearson Corr")
    )

    fig.update_layout(
        title=dict(
            text="<b>Daily Returns Correlation Heatmap</b>",
            x=0.02,
            y=0.96,
            font=dict(size=15, color='#F3F4F6')
        ),
        paper_bgcolor='#1E222D',
        plot_bgcolor='#131722',
        font=dict(color='#E0E3EB', family='sans-serif'),
        margin=dict(l=45, r=30, t=55, b=45)
    )
    fig.update_traces(hovertemplate="Asset 1: %{x}<br>Asset 2: %{y}<br>Correlation: %{z:.3f}<extra></extra>")
    return fig


def create_drawdown_fig(daily_returns: pd.DataFrame, portfolio_returns: pd.Series) -> go.Figure:
    """Create interactive underwater drawdown area chart."""
    wealth_index = (1 + daily_returns).cumprod()
    peaks = wealth_index.cummax()
    drawdowns = (wealth_index - peaks) / peaks * 100

    port_wealth = (1 + portfolio_returns).cumprod()
    port_peak = port_wealth.cummax()
    port_drawdown = (port_wealth - port_peak) / port_peak * 100

    fig = go.Figure()

    # Asset drawdowns
    for col in drawdowns.columns:
        fig.add_trace(go.Scatter(
            x=drawdowns.index,
            y=drawdowns[col],
            mode='lines',
            name=col,
            opacity=0.4,
            hovertemplate=f"<b>{col}</b><br>Date: %{{x|%Y-%m-%d}}<br>Drawdown: %{{y:.2f}}%<extra></extra>",
            line=dict(width=1.2)
        ))

    # Portfolio drawdown filled area
    fig.add_trace(go.Scatter(
        x=port_drawdown.index,
        y=port_drawdown,
        mode='lines',
        name='PORTFOLIO',
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.25)',
        line=dict(color='#EF4444', width=2.5),
        hovertemplate="<b>PORTFOLIO</b><br>Date: %{x|%Y-%m-%d}<br>Drawdown: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="<b>Drawdown Trajectory (Underwater Risk Chart)</b>",
            x=0.02,
            y=0.96,
            font=dict(size=15, color='#F3F4F6')
        ),
        yaxis_title="Drawdown (%)",
        xaxis_title="Date",
        **DARK_LAYOUT
    )
    return fig
