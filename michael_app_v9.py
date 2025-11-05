#type: ignore

"""Visualising cumulative returns and rolling betas"""
import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd

st.set_page_config(page_title="MIS20080 - Project", layout="wide")

# --- User input ---
ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()
if ticker == "":
    st.error("Please enter a valid ticker symbol.")
    st.stop()

# --- Industry info ---
def get_ticker_industry(ticker):
    ticker_info = yf.Ticker(ticker).info
    return ticker_info.get("industry", "Industry not found")

industry = get_ticker_industry(ticker)
st.write(f"The industry for ticker {ticker} is: {industry}")

# --- Download data ---
SPX_data = yf.download(["^GSPC"], period="5y", auto_adjust=False, progress=False)
ticker_data = yf.download([ticker], period="5y", auto_adjust=False, progress=False)
if ticker_data is None or ticker_data.empty:
    st.error(f"Ticker {ticker} not found.")
    st.stop()

# --- Daily returns ---
SPX_returns = SPX_data["Adj Close"].pct_change().dropna()
ticker_returns = ticker_data["Adj Close"].pct_change().dropna()

# --- Cumulative returns plot ---
cumulative_SPX_returns = (1 + SPX_returns).cumprod() - 1
cumulative_ticker_returns = (1 + ticker_returns).cumprod() - 1

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cumulative_ticker_returns.index,
    y=cumulative_ticker_returns.squeeze(),
    mode="lines",
    name=f"{ticker} Cumulative Returns",
    line=dict(color="orange")
))
fig.add_trace(go.Scatter(
    x=cumulative_SPX_returns.index,
    y=cumulative_SPX_returns.squeeze(),
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

# --- 5-year Beta calculation ---
Ri = ticker_data["Adj Close"].pct_change().dropna().to_numpy()
Rm = SPX_data["Adj Close"].pct_change().dropna().to_numpy()

if len(Ri) != len(Rm):
    print("Dates do not align")
else:
    N = len(Ri)

Ri_mean = Ri.mean()
Rm_mean = Rm.mean()

Rm_var = Rm.var(ddof=1)

accum = 0
for ri, rm in zip(Ri, Rm):
    accum += (ri - Ri_mean) * (rm - Rm_mean)
Covar = accum / (N - 1)

Beta = Covar / Rm_var
st.write(f"The 5-year Beta for {ticker} is {Beta}")

# --- Rolling Beta (60-day window) ---
window = 60
ri = ticker_returns.squeeze().rename("Ri")
rm = SPX_returns.squeeze().rename("Rm")
ret = pd.concat([ri, rm], axis=1).dropna()

rolling_cov = ret["Ri"].rolling(window).cov(ret["Rm"])
rolling_var = ret["Rm"].rolling(window).var()
rolling_beta = (rolling_cov / rolling_var).dropna()

fig_beta = go.Figure()
fig_beta.add_trace(go.Scatter(
    x=cumulative_ticker_returns.index,
    y=rolling_beta.squeeze(),
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
