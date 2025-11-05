import yfinance as yf
import numpy as np
import streamlit as st
import matplotlib as mp

ticker = "AAPL"
competitor = st.text_input("Enter competitor ticker: ").strip().upper()
if ticker == "":
    st.error("Please enter a valid ticker symbol.")
    st.stop()

ticker_data = yf.download([ticker], period = "5y", auto_adjust=False)
#competitor_data = yf.download([competitor], period = "5y", auto_adjust=False)

#Mean Daily Returns
adj_close = ticker_data["Adj Close"].iloc[:,0]
adj_close_comp = competitor_data["Adj Close"].iloc[:,0]
#This retrieves data from first column only
adjdailyreturns = adj_close.pct_change().dropna() 
adjdailyreturns_comp = adj_close_comp.pct_change().dropna() 
#dropna() removes all blank entries
cumulative_returns = (adj_close.iloc[-1]/adj_close.iloc[0]) - 1
cumulative_returns_comp = (adj_close_comp.iloc[-1]/adj_close_comp.iloc[0]) - 1



daily_returns = (adjdailyreturns) 
daily_returns_comp = (adj_close_comp)

#print(f"AAPL's mean daily return is {pctmeandailyreturn:.2f}%")


def meandailyret(daily_returns):
    """
    calculates mean daily return of input
    can then be called for competitor
    """
    mean_return = np.mean(daily_returns)
    return mean_return*100


#Standard Deviation 
#stdev_daily = np.std(daily_returns, ddof = 1)
#stdev_annual = stdev_daily*np.sqrt(252)
#stdev_pct = stdev_annual*100
#print(f"AAPL's Standard Deviation is {stdev_pct:.2f}%")

def stdev(daily_returns):
    """
    calculates daily stdev 
    multiply by sqrt(252) to convert to annual
    """

    daily_stdev = np.std(daily_returns, ddof=1)
    annualstdev = daily_stdev*np.sqrt(252)
    annualstdevpct = annualstdev*100
    return annualstdevpct

annualstdevpct = stdev(daily_returns)

print(f"AAPL's daily stdev: {annualstdevpct:.2f}%")

#VaR
#daily - Z*sd

#def VaR()