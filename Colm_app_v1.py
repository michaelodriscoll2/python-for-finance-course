import yfinance as yf
import streamlit as sl
ticker = "AAPL"
ticker_data = yf.download([ticker],period="1y",auto_adjust=False)



#Mean Daily returns calculation
adj_close = ticker_data["Adj Close"].iloc[:,0] #ts gets 1st and only ticker column
adjdaily_returns = adj_close.pct_change().dropna()

daily_returns = (adjdaily_returns)

sum_return = 0  #accumulator variable
for i in daily_returns:
    sum_return += i
mean_daily_returns = sum_return/len(daily_returns)
percentagemean_daily_return = mean_daily_returns*100
print(percentagemean_daily_return)


#Standard Deviation Calculation
sum_sqd_diff = 0 
for r in percentagemean_daily_return:
    sum_sqd_diff += (r - mean_daily_returns) ** 2
    
var = sum_sqd_diff/(len(percentagemean_daily_return)-1)
stdev = var ** 0.5

print(stdev)




#Sharpe Ratio calculation