# Stock Analysis and Portfolio Optimization Dashboard
# Created by: Michael O'Driscoll, Jack Lappin, Colm Enright and Zach Treacy

This project is a Streamlit-powered interactive dashboard for analyzing individual stocks, comparing competitors, asessing risk metrics and optimizing portfolio weightings using financial metrics and the Capital Asset Pricing Model (CAPM). It integrates real-time data from Yahoo Finance and visualizes key performance indicators using Plotly. It's goal is to allow the user to make an informed investment decison by providing key information for a stock they wish to include in their portfolio.

The features of this dashboard are:

Stock Ticker Analysis: Input any stock ticker to view its cumulative returns, beta industry classification, and any recent related headlines.
Competitor Comparisons: Compare daily returns, volatility, and Value at Risk (VaR) between a selected stock and its competitor.
CAPM Analysis: Calculate expected returns using the CAPM formula across daily, quarterly, and annual timeframes.
Interactive Charts: Visualize cumulative returns, daily returns, rolling beta, moving averages, expected annual returns and optimized portfolio weights.
Portfolio Building: Add tickers to a portfolio and optimize it using Sharpe Ratio maximization.

The necessary installations/libraries include:

yfinance
streamlit
plotly
numpy
pandas
matplotlib
scipy

Key Objects & Functions Descriptions:

Objects:              | Description
----------------------|------------------------------------------------------------
ticker, competitor    | User-input stock symbols
portfolio_tickers     | Session state list of tickers
SPX_returns           | Daily returns for S&P 500 benchmark
ticker_returns        | Daily returns for selected stock
Beta                  | 5-year beta value
rolling_beta          | 60-day rolling beta
rf                    | Annual risk-free rate
log_returns           | Logarithmic returns for portfolio assets
cov_matrix            | Annualized covariance matrix
optimal_weights       | Optimized asset weights
capm_er_daily         | CAPM expected daily stock return
capm_er_quarterly     | CAPM expected quarterly stock return
capm_er_annual        | CAPM expected annual stock return
                      
Functions:            |
expected_returns()    | Computes expected portfolio return
standard_deviation()  | Computes portfolio volatility
sharpe_ratio()        | Computes Sharpe Ratio
neg_sharpe_ratio()    | Negative Sharpe Ratio for optimization

How It Works:

1. User Inputs
   
ticker: Main stock ticker for analysis.
competitor: Optional competitor ticker for comparison.
rf: Annual risk-free rate input for CAPM and Sharpe Ratio calculations.
portfolio_tickers: List of tickers added to the portfolio via checkbox.

2. Data Retrieval
   
Uses yfinance to download historical price data for tickers and benchmark.

3. Metrics are computed and displayed and portfolio optimization is  carried out.    

Note:
The app can be run in VS Code via the python terminal (base (3.13.5) Conda environment) using the command: streamlit run Final_Version_v1.py
Alternatively, it can be accessed directly on Streamlit with the following link:
