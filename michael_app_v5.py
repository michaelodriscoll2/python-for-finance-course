"""First attempt at beta calc"""
import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
import numpy as np


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
    
SPX_data = yf.download(["^GSPC"], period="1y", auto_adjust=False)
ticker_data = yf.download([ticker], period="1y", auto_adjust=False)
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

"""Now calculating rolling beta of the stock vs SPX"""
Ri = np.array(ticker_returns)
Rm = np.array(SPX_returns)

#Sample means
Ri_mean = np.mean(Ri)
Rm_mean = np.mean(Rm)

#We are only observing 1y of data so we have to take the sample mean i.e 1 degree of freedom
Ri_var = np.var(Ri,ddof=1)
Rm_var = np.var(Rm,ddof=1)



#Covar calc
print(len(Ri))
print(len(Rm))

if len(Ri) != len(Rm):
     print("Dates do not align")
else: N = len(Ri)



accum=0
for ri,rm in zip(Ri,Rm):
    accum += (ri-Ri_mean)*(rm-Rm_mean)
Covar = accum/(N-1)

print(Covar)


#Beta calc = Cov(Ri,Rm)/Var(Rm)
Beta = Covar/Rm_var
print(Beta)     
