"""Will try and make it so that the stock entered will automatically determine GICS industry"""
import yfinance as yf
import streamlit as st
import plotly.graph_objs as go


st.set_page_config(page_title="MIS20080 - Project",layout="wide")
st.title("MIS20080 - Project")

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
    legend_title="Legend",
    template="plotly_white",
    hovermode="x unified",
    height=500,)
st.plotly_chart(fig, use_container_width=True)
