# 📈 Stock Portfolio Risk & Performance Dashboard

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/web-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/charts-Plotly-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive, quantitative financial web application and python dashboard designed for evaluating multi-asset portfolio risk and return metrics. Built specifically for financial analyst and quantitative software engineering interview preparation (targeting firms like **Goldman Sachs, Morgan Stanley, J.P. Morgan**).

The application features a modern dark-themed web interface (built with **Streamlit** and **Plotly**), real-time control panels, interactive charts, metric cards, and downloadable CSV reports.

---

## 🌟 Key Features

- **Interactive Financial Web UI**: Modern dark theme (`#0E1117` glassmorphic styling) with interactive Plotly charts, hover inspect, date range sliders, and metric cards.
- **Global Market Ingestion**: Fetches historical adjusted daily prices using `yfinance` with cross-market trading calendar alignment (e.g., handling US vs. Indian NSE holiday mismatches).
- **Comprehensive Risk & Return Metrics**:
  - **Daily & Cumulative Returns**: Compounded growth tracking.
  - **Annualized Return (CAGR)**: 252-day annualized growth rate.
  - **Annualized Volatility**: Returns standard deviation scaled by $\sqrt{252}$.
  - **Sharpe Ratio**: Excess return over configurable risk-free rates ($R_f = 4.0\%$ US, $6.5\%$ India).
  - **Maximum Drawdown (MDD)**: Peak-to-trough downside risk and underwater duration analysis.
  - **Correlation Matrix**: Asset return correlation matrix for diversification analysis.
- **Custom Weighting & Equal Weighting**: Supports both Equal-Weighted ($1/N$) and custom asset allocation vectors with live normalization.
- **Interactive Visualizations**:
  1. *Normalized Price Performance (Base 100)*.
  2. *Cumulative Growth (Portfolio vs. Constituents)*.
  3. *Rolling 30-Day Annualized Volatility*.
  4. *Daily Return Correlation Heatmap*.
  5. *Underwater Drawdown Risk Chart*.
- **1-Click Cloud Deployment**: Ready to deploy live for free on Streamlit Community Cloud for resume inclusion.

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/stock-portfolio-risk-dashboard.git
cd stock-portfolio-risk-dashboard
pip install -r requirements.txt
```

### 2. Launch the Web Application
Start the interactive Streamlit web dashboard in your browser:
```bash
streamlit run app.py
```
*(The web dashboard will automatically open at `http://localhost:8501`)*

### 3. Run the CLI Dashboard (Terminal Mode)
```bash
python main.py
```

---

## 📐 Financial Formulas & Quantitative Logic (Interview Cheat Sheet)

| Financial Metric | Mathematical Formula | Key Concept / Interview Explanation |
| :--- | :--- | :--- |
| **Simple Daily Return** | $r_t = \frac{P_t - P_{t-1}}{P_{t-1}}$ | Percentage daily price change. Simple returns are linearly additive across assets for portfolio weighting. |
| **Portfolio Return** | $r_{\text{port}, t} = \sum_{i=1}^N w_i r_{i, t}$ | Weighted linear combination of individual stock returns where $\sum w_i = 1.0$. |
| **Annualized Return (CAGR)** | $\text{CAGR} = (1 + R_{\text{cum}})^{\frac{252}{N}} - 1$ | Compound Annual Growth Rate standardizing overall growth across a 252-trading-day annual timeline. |
| **Annualized Volatility** | $\sigma_{\text{annual}} = \sigma_{\text{daily}} \times \sqrt{252}$ | Total investment risk. Scaled by $\sqrt{252}$ under the assumption of independent daily variance ($\sigma^2_{\text{annual}} = 252 \cdot \sigma^2_{\text{daily}}$). |
| **Sharpe Ratio** | $\text{Sharpe} = \frac{\text{CAGR} - R_f}{\sigma_{\text{annual}}}$ | Measures excess return per unit of total risk. Sharpe $> 1.0$ is considered good; Sharpe $> 2.0$ is exceptional. |
| **Maximum Drawdown** | $\text{Drawdown}_t = \frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}$ | Peak-to-trough decline. Represents worst historical loss from buying at the top before recovery. |
| **Correlation** | $\rho_{X, Y} = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y}$ | Pearson correlation of daily returns. Lower or negative correlation enables Modern Portfolio Theory (MPT) diversification benefits. |

---

## 📁 Repository Structure

```
new trading project/
├── app.py               # Streamlit interactive Web Application frontend & controller
├── web_visualizations.py# Plotly interactive dark-themed chart generator
├── data_fetcher.py      # Download, clean, and align daily price data from yfinance
├── metrics.py           # Core financial risk & return calculations for stocks & portfolio
├── visualizations.py    # Matplotlib static generator for CLI/PNG exports
├── main.py              # CLI driver supporting custom tickers, weights, risk-free rate
├── requirements.txt     # Python dependencies
├── README.md            # Comprehensive project documentation
├── .streamlit/          # Streamlit dark financial theme configuration
│   └── config.toml
└── output/              # Auto-generated PNG analytical charts (from CLI mode)
```

---

## 📜 License
This project is open source and available under the [MIT License](LICENSE).
