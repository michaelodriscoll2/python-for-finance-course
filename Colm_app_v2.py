import yfinance as yf
import streamlit as sl
import numpy as np
ticker = "AAPL"
ticker_data = yf.download([ticker],period="1y", auto_adjust=False)

#Mean Daily Returns 
adj_close = ticker_data["Adj Close"].iloc[:,0] #gets 1st and only ticker column
adjdailyreturns = adj_close.pct_change().dropna()
cumulative_return = (adj_close.iloc[-1]/adj_close.iloc[0]) - 1


daily_returns = (adjdailyreturns)
sum_return = 0 #accumulator variable
for i in daily_returns:
    sum_return += i
mean_daily_return = sum_return/len(daily_returns)
pctmean_daily_return = mean_daily_return*100
#print(pctmean_daily_return)
print(f"AAPL's mean daily return: {pctmean_daily_return:.2f}%")

#Standard Deviation 
sum_squared_diff = 0
for r in adjdailyreturns:
    sum_squared_diff += (r - mean_daily_return)**2

variance_daily = sum_squared_diff/(len(daily_returns)-1)
sd_daily = variance_daily**0.5
variance = variance_daily*np.sqrt(252)
standard_deviation = variance**0.5
sd_pct = standard_deviation*100
#print(variance)
#print(standard_deviation)
print(f"AAPL's standard deviation: {sd_pct:.2f}% ")

#Sharpe Ratio
rf_annual = 0.049
rf_daily = rf_annual / 252

sharpe_daily = (mean_daily_return - rf_daily)/sd_daily
sharpe = sharpe_daily*np.sqrt(252)

print(f"AAPL's daily Sharpe ratio: {sharpe_daily:.2f}")
print(f"AAPL's annualised Sharpe ratio: {sharpe:.2f}")


#Value at Risk
#Z x stdev x mean daily return
#95% confidence -> Z = 1.645
z = 1.645

vatr_daily = (z*sd_daily) - mean_daily_return 
vatr_annual = vatr_daily*np.sqrt(252)
vatr_annual_pct = vatr_annual*100

print(f"AAPL's Annual Value at Risk is {vatr_annual_pct:.2f}")
#print(vatr_daily*100)
#print(f"daily stdev {sd_daily}")

#Displaying metrics
sl.subheader(f"Risk metrics - AAPL")
c1, c2, c3, c4 = sl.columns(4)
c1.metric("Mean Daily Return", f"{pctmean_daily_return:.4}%")
c2.metric("Standard Deviation", f"{sd_pct:.2}")
c3.metric("Sharpe Ratio", f"{sharpe:.2}%")
c4.metric("Value at Risk Annual, 95 confidence", f"{vatr_annual_pct}%")