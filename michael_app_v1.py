import yfinance as yf
import streamlit as st #Will use this for dashboard launch


ticker = st.text_input("Enter Stock Ticker", "AAPL").upper() #.upper() to ensure ticker is uppercase -> won't cause issues when calling yf 

Gics_Industries = ["Energy","Materials","Industrials","Consumer Discretionary","Consumer Staples","Health Care","Financials","Information Technology","Communication Services","Utilities","Real Estate"]
#May be able to in later iterations make it so that calling the stock will automatically get the indsutry
#Not sure if yfinance has this ability 

#Need to get data for SPX and "ticker"
SPX_data = yf.download(["^GSPC"], period="1y", auto_adjust=True)
ticker_data = yf.download([ticker], period="1y", auto_adjust=True)

#Returns calculation
SPX_returns = SPX_data['Close'].pct_change().dropna() # type: ignore
ticker_returns = ticker_data['Close'].pct_change().dropna() # type: ignore

print(SPX_returns.tail())

cumulative_SPX_returns = (1 + SPX_returns).cumprod() - 1 #cumprod() is just a function to calculate cumulative returns
cumulative_ticker_returns = (1 + ticker_returns).cumprod() - 1

