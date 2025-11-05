#type: ignore

import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd

st.set_page_config(page_title="MIS20080 - Project", layout="wide")

# User input
ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()
if ticker == "":
    st.error("Please enter a valid ticker symbol.")
    st.stop()

# Industry info
def get_ticker_industry(ticker):
    """Safely get industry info; return 'Unknown' if ticker invalid."""
    try:
        ticker_info = yf.Ticker(ticker).info
        industry = ticker_info.get("industry", "Industry not found")
        return industry
    except Exception as e:
        st.error(f"Could not retrieve info for ticker '{ticker}'. Please check the symbol.")
        return "Unknown"

industry = get_ticker_industry(ticker)
if industry == "Unknown":
    st.stop()
st.write(f"The industry for ticker {ticker} is: {industry}")

# Download data
SPX_data = yf.download(["^GSPC"], period="5y", auto_adjust=False, progress=False)
ticker_data = yf.download([ticker], period="5y", auto_adjust=False, progress=False)

if ticker_data is None or ticker_data.empty:
    st.error(f"Ticker {ticker} not found.")
    st.stop()

# Daily returns (ensure 1-D Series)
SPX_returns   = SPX_data["Adj Close"].pct_change().dropna().squeeze()
ticker_returns = ticker_data["Adj Close"].pct_change().dropna().squeeze()

# Cumulative returns
cumulative_SPX_returns    = (1 + SPX_returns).cumprod() - 1
cumulative_ticker_returns = (1 + ticker_returns).cumprod() - 1

# Plot cumulative returns
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cumulative_ticker_returns.index,
    y=cumulative_ticker_returns,
    mode="lines",
    name=f"{ticker} Cumulative Returns",
    line=dict(color="orange")
))
fig.add_trace(go.Scatter(
    x=cumulative_SPX_returns.index,
    y=cumulative_SPX_returns,
    mode="lines",
    name="S&P 500 Cumulative Returns",
    line=dict(color="blue")
))
fig.update_layout(
    title=f"{ticker} vs S&P 500 Cumulative Returns",
    xaxis_title="Date",
    yaxis_title="Cumulative Returns",
    yaxis=dict(tickformat=".0%"),
    legend_title="Legend",
    template="plotly_white",
    hovermode="x unified",
    height=300,
)
st.plotly_chart(fig, use_container_width=True)

# 5-year Beta (align dates using a joined frame)
ret = pd.concat(
    [ticker_returns.rename("Ri"), SPX_returns.rename("Rm")],
    axis=1
).dropna()
Ri = ret["Ri"].values
Rm = ret["Rm"].values
N = len(ret)

Ri_mean = Ri.mean()
Rm_mean = Rm.mean()

Rm_var = Rm.var(ddof=1)
Covar = ((Ri - Ri_mean) * (Rm - Rm_mean)).sum() / (N - 1)
Beta = Covar / Rm_var
st.write(f"The 5-year Beta for {ticker} is {Beta:.3f}")

# Rolling Beta (60-day window)
window = 60
rolling_cov  = ret["Ri"].rolling(window).cov(ret["Rm"])
rolling_var  = ret["Rm"].rolling(window).var()
rolling_beta = (rolling_cov / rolling_var).dropna()

fig_beta = go.Figure()
fig_beta.add_trace(go.Scatter(
    x=rolling_beta.index,   # <-- use rolling_beta's index
    y=rolling_beta,
    mode="lines",
    name=f"{ticker} Rolling Beta ({window}-day window)",
    line=dict(color="orange")
))
fig_beta.add_hline(
    y=1.0, line_dash="dot",
    annotation_text="β = 1 (market)",
    annotation_position="top left"
)
fig_beta.update_layout(
    title=f"{ticker} Rolling Beta vs S&P 500 ({window}-day window)",
    xaxis_title="Date",
    yaxis_title="Beta (unitless)",
    template="plotly_white",
    hovermode="x unified",
    height=300,
)
st.plotly_chart(fig_beta, use_container_width=True)

# ================================
# Colm (below your app)
# ================================
st.subheader("📊 Competitor Comparison & Risk Metrics")
competitor = st.text_input("Enter Competitor's Stock Ticker", "NVDA").upper()
if competitor == "":  # <-- fixed (was checking ticker)
    st.error("Please enter a valid competitor ticker symbol.")
    st.stop()

competitor_data = yf.download([competitor], period="5y", auto_adjust=False, progress=False)
competitor_returns = competitor_data["Adj Close"].pct_change().dropna().squeeze()

# Mean daily returns (percent)
mean_ticker_returns = ticker_returns.mean()
mean_comp_returns   = competitor_returns.mean()
st.markdown(f"{ticker}'s mean daily return is {mean_ticker_returns:.4%}")
st.markdown(f"{competitor}'s mean daily return is {mean_comp_returns:.4%}")

# Standard Deviation (annualized %), ensure scalars then format as %
ticker_std_daily = float(np.std(ticker_returns.values, ddof=1))
comp_std_daily   = float(np.std(competitor_returns.values, ddof=1))

ticker_annual_std = ticker_std_daily * np.sqrt(252)
comp_annual_std   = comp_std_daily * np.sqrt(252)

st.markdown(f"{ticker}'s annual standard deviation is {ticker_annual_std:.2%}")
st.markdown(f"{competitor}'s annual standard deviation is {comp_annual_std:.2%}")


#VaR -> Mean daily return - (Std*Zscore)
z_score = 1.645

ticker_vatr_daily = (z_score*ticker_std_daily) - mean_ticker_returns
ticker_vatr_annual = ticker_vatr_daily*np.sqrt(252)
ticker_vatr_annual_pct = ticker_vatr_annual*100

comp_vatr_daily = (z_score*comp_std_daily) - mean_comp_returns
comp_vatr_annual = comp_vatr_daily*np.sqrt(252)
comp_vatr_annual_pct = comp_vatr_annual*100

st.markdown(f"{ticker}'s Annual Value at Risk is {ticker_vatr_annual_pct:.2f}%")
st.markdown(f"{competitor}'s Annual Value at Risk is {comp_vatr_annual_pct:.2f}%")













