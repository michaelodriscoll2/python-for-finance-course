"""Visualising the rolling betas"""
import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd 

st.set_page_config(page_title="MIS20080 - Project",layout="wide")

ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()
if ticker == "":
    st.error("Please enter a valid ticker symbol.")
    st.stop()

    
def get_ticker_industry(ticker):
        ticker_info = yf.Ticker(ticker).info
        return ticker_info.get("industry", "Industry not found") # .get() is safer than ['key'] - from notes week 7 
industry = get_ticker_industry(ticker)
st.write(f"The industry for ticker {ticker} is: {industry}")
    
SPX_data = yf.download(["^GSPC"], period="5y", auto_adjust=False)
ticker_data = yf.download([ticker], period="5y", auto_adjust=False)
if ticker_data is None or ticker_data.empty:
    st.error(f"Ticker {ticker} not found.") #Error if ticker is not found by yf- happens loads
    st.stop()

SPX_returns = SPX_data['Adj Close'].pct_change().dropna() # type: ignore
ticker_returns = ticker_data['Adj Close'].pct_change().dropna() # type: ignore

#Calculating Cumulative Returns
cumulative_SPX_returns = (1 + SPX_returns).cumprod() - 1
cumulative_ticker_returns = (1 + ticker_returns).cumprod() - 1

#Graphing ticker vs SPX
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cumulative_ticker_returns.index,
    y=cumulative_ticker_returns.squeeze(),
    mode="lines",
    name=f"{ticker} Cumulative Returns",
    line=dict(color="orange")))
fig.add_trace(go.Scatter(
    x=cumulative_SPX_returns.index,
    y=cumulative_SPX_returns.squeeze(),
    mode="lines",
    name="S&P 500 Cumulative Returns",
    line=dict(color="blue")))
fig.update_layout(
    title=f"{ticker} vs S&P 500 Cumulative Returns",
    xaxis_title="Date",
    yaxis_title="Cumulative Returns",
    yaxis=dict(tickformat=".0%"),
    legend_title="Legend",
    template="plotly_white",
    hovermode="x unified",
    height=300,)
st.plotly_chart(fig, use_container_width=True)

#Now calculating rolling beta of the stock vs SPX 
     
Ri = np.array(ticker_returns)
Rm = np.array(SPX_returns)
if len(Ri) != len(Rm):
     print("Dates do not align")

Ri_mean = np.mean(Ri)
Rm_mean = np.mean(Rm)
Ri_var = np.var(Ri,ddof=1)
Rm_var = np.var(Rm,ddof=1)
if len(Ri) != len(Rm):
     print("Dates do not align")
else: N = len(Ri)
accum=0
for ri,rm in zip(Ri,Rm):
    accum += (ri-Ri_mean)*(rm-Rm_mean)
Covar = accum/(N-1)
#Beta calc = Cov(Ri,Rm)/Var(Rm)
Beta = Covar/Rm_var


#Creating one big for loop window size = 50 days
rolling_betas = []
window = 50
for i in range(window, len(Ri)):
    Ri_window = Ri[i-window:i]
    Rm_window = Rm[i-window:i]

    #Sample means
    Ri_rolling_mean = np.mean(Ri_window)
    Rm_rolling_mean = np.mean(Rm_window)

    #We are only observing 5y of data so we have to take the sample mean i.e 1 degree of freedom
    Ri_rolling_var = np.var(Ri_window,ddof=1)
    Rm_rolling_var = np.var(Rm_window,ddof=1)

    #Covar calc
    accum=0
    for ri,rm in zip(Ri,Rm):
        accum += (ri-Ri_rolling_mean)*(rm-Rm_rolling_mean)
    Covar = accum/(window-1)
    #Beta calc = Cov(Ri,Rm)/Var(Rm)
    rolling_Beta_value = Covar/Rm_rolling_var
    rolling_betas.append(rolling_Beta_value)   

#Graphing the rolling beta
dates_for_betas = ticker_returns.index[window:]  # same length as rolling_betas


fig_beta = go.Figure()
fig_beta.add_trace(go.Scatter(
    x=cumulative_ticker_returns.index,
    y=rolling_betas,   
    mode="lines",
    name=f"{ticker} Rolling Beta (50d)"
))
fig_beta.add_hline(y=1.0, line_dash="dot",
                   annotation_text="β = 1 (market)",
                   annotation_position="top left")
fig_beta.update_layout(
    title=f"{ticker} Rolling Beta vs S&P 500 (50 trading days)",
    xaxis_title="Date",
    yaxis_title="Beta (unitless)",
    template="plotly_white",
    height=320,
    margin=dict(l=10, r=10, t=40, b=10)
)
st.plotly_chart(fig_beta, use_container_width=True)

st.write(f"The 5 year Beta value for {ticker} is {Beta}")


 