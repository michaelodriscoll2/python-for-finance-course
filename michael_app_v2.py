import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="MIS20080 - Project", layout="wide")
st.title("MIS20080 - Project")

ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()

Gics_Industries = [
    "Energy","Materials","Industrials","Consumer Discretionary","Consumer Staples",
    "Health Care","Financials","Information Technology","Communication Services",
    "Utilities","Real Estate"
]
Industries = st.selectbox("Select Industry", Gics_Industries)

# --- Data ---
SPX_data = yf.download(["^GSPC"], period="1y", auto_adjust=False)
ticker_data = yf.download([ticker], period="1y", auto_adjust=False)

SPX_returns = SPX_data["Adj Close"].pct_change().dropna()        # type: ignore
ticker_returns = ticker_data["Adj Close"].pct_change().dropna()  # type: ignore

# Cumulative returns
cumulative_SPX_returns = (1 + SPX_returns).cumprod() - 1
cumulative_ticker_returns = (1 + ticker_returns).cumprod() - 1

fig, ax = plt.subplots(figsize=(10, 6)) 
ax.plot(cumulative_SPX_returns.index, cumulative_SPX_returns, label='S&P 500', color='blue') 
ax.plot(cumulative_ticker_returns.index, cumulative_ticker_returns, label=ticker, color='orange') 
ax.set_title(f'Cumulative Returns: {ticker} vs S&P 500') 
ax.set_xlabel('Date') 
ax.set_ylabel('Cumulative Return') 
ax.legend() 
st.pyplot(fig) 

