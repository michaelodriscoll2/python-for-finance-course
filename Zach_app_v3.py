#%%
#importing libraries and creating environment
import yfinance as yf
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st 
import plotly.graph_objects as go

#--------------------------------------------------------------------------#

#V3 Main Changes:#
#--------------------------------------------------------------------------#
#change to use adjusted close only
#improved the two daily returns graphs to both be the same chart for better comparison, used plotly instead of streamlit line chart
#added in quarterly and daily capm returns 
#data period chnaged to 5 years
#removed csv download button as not needed for single asset
#equal weights code added

#--------------------------------------------------------------------------#

# first set the page configuration as having this code below returned an error
st.set_page_config(page_title="Expected Portfolio Returns", layout="wide")

# now add in dashboard title 
st.title("Expected Portfolio Returns Analysis")



# now get stock data for chosen portfolio from yfinance
tkr = st.text_input("Enter Stock Ticker", "AAPL").upper() #uppercase tickers to match yfinance format
tkr_data = yf.download([tkr], period = '5y', auto_adjust= True)['Close'] #ensure using adjusted close prices

#obtaining data from benchmark index (S&P 500)
bm_data = yf.download(["^GSPC"], period = '5y', auto_adjust= True)['Close'] #ensure using adjusted close prices

#coding for errors if ticker not found or no data available
if tkr_data.empty: 
    st.error("Ticker not found or no data available. Please check the ticker symbol and try again.") 
    st.stop()


#displaying company name in streamlit app 
tkr_obj = yf.Ticker(tkr)
ticker_info = tkr_obj.info 
if ticker_info:
    st.write(f"Company Name: {ticker_info['longName']}")
else:
    st.write("Company Name: Not Found")


#calculating daily returns for both portfolio and benchmark
# portfolio daily returns first: 
pf_returns = tkr_data.pct_change().dropna()

# benchmark daily returns next (same method as above):
bm_returns = bm_data.pct_change().dropna()

#print results to console for verification
print(pf_returns)
print(bm_returns)

# handle if only singular ticker downloaded (would return a series not a dataframe)
try:

    if isinstance(pf_returns, pd.Series):
        pf_returns = pf_returns.to_frame(tkr[0])

    if isinstance(bm_returns, pd.Series):
        bm_returns = bm_returns.to_frame("S&P500")

except Exception as e:
    st.error(f"An error occurred while processing the data: {e}")
    st.stop()
    
# add in interactive sliders and moving average plots (only when data exists)
if pf_returns.empty or bm_returns.empty:
    st.warning("Not enough data to display interactive return charts.")
else:
    # choosing window based on overlapping length so both series have values
    n_max = max(1, min(len(pf_returns), len(bm_returns))) #the downloaded data is for 5 trading years so should show last 1260 days max

     #interactive sliders for days to show and moving average length
    show_days = st.slider("Show Last X Trading Days", min_value=1, max_value=n_max, value= 252)
    ma_window = st.slider("Moving Average Length (Days)", min_value=0, max_value=60, value=30)

    # take tail of each series and align by date to create dataframe for plotting
    pf_display = pf_returns.tail(show_days)
    bm_display = bm_returns.tail(show_days)

    #account for if pf_display or bm_display is a single-column Data Frame, converting them to a series to avoid errors
    if isinstance(pf_display, pd.DataFrame):
        pf_display = pf_display.iloc[:,0]
 #lines 94 to 101 were changed in v3 to match the style of session10.ipynb
    if isinstance(bm_display, pd.DataFrame):
        bm_display = bm_display.iloc[:,0]

    # create dataframe for plotting and drop NaNs to avoid errors
    df_plot = pd.concat([pf_display.rename(tkr), bm_display.rename("S&P500")], axis=1).dropna()

    # add moving averages if requested
    if ma_window > 0:
        df_plot[f"{tkr}_MA"] = df_plot[tkr].rolling(window=ma_window).mean()
        df_plot["S&P500_MA"] = df_plot["S&P500"].rolling(window=ma_window).mean()


#---------------------------------------------------------------------------------------------#
# edit code from here - the stuff above this is gonna be already done by i think Michael , but i have it in to make my model work in my personal app
#---------------------------------------------------------------------------------------------#

    # portfolio vs benchmark chart using plotly 
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot[tkr], mode="lines", name=tkr,
        line=dict(color="orange", width=1)
    ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["S&P500"], mode="lines", name="S&P500",
        line=dict(color="blue", width=1)
    ))

    if ma_window > 0:
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot[f"{tkr}_MA"], mode="lines", name=f"{tkr} MA",
            line=dict(color="red", width=1)
        ))
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["S&P500_MA"], mode="lines", name="S&P500 MA",
            line=dict(color="lime", width=1)
        ))

    fig.update_layout(
        title=f"Portfolio vs S&P500 Daily Returns (last {show_days} days)",
        xaxis_title="Date",
        yaxis_title="Daily return",
        hovermode="x unified",
        height=600
    )
    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)
    


# %% CAPM expected return calculations
Trading_days = 252 # assuming 252 trading days in a year
num_assets = len(tkr)
eq_weights = np.array([1/num_assets] * num_assets) #code for equal portfolio weightings - not yet integrated into code
#see jacks code for optimized weights

#add in section subheader into streamlit app
st.subheader("CAPM Model")

# allow user to set risk-free rate (annual)
#risk free rate is defaulted to 2% but user can change it betwween 0% and 4%
rf = st.number_input("Choose Annual Risk-Free Rate (0 to 4%)", min_value=0.0, max_value= 0.04, value=0.02, step=0.001, format="%.4f")

# align asset and market returns on overlapping dates
combined = pd.concat([pf_returns, bm_returns], axis=1).dropna()
combined.columns = [tkr, "S&P500"] #tkr is the asset, S&P500 is the market

#wrap CAPM code in if statement to avoid crashes
if combined.empty:
    st.warning("Not enough overlapping returns to compute CAPM. Check data/period.") #warning message if not enough data to avoid crashes
else:    
    asset = combined[tkr]              # the portfolio returns
    market = combined['S&P500']        # the benchmark returns


    # Calculate beta as covariance(asset, market) / variance(market)

    beta_cov = np.cov(asset, market)[0, 1] / np.var(market)

    # make loop here to do it for each stock  in portfolio and multiply by weights


    # Have market annual arithmetic return for comparison
    market_annual_arith = market.mean() * Trading_days


 # CAPM expected return formula is risk free rate + beta * (market return - risk free rate)
    capm_er_annual = rf + beta_cov * (market_annual_arith - rf)

 # calculate CAPM expected return on a annual, daily and quarterly scale
 # Daily CAPM expected return: 
 #(obtain each component of formula first)

    Trading_days_quarter = 63  # assuming 252 trading days in a  year and dividing by 4

#now get quarterly and daily risk free rates from annual risk free rate calculated above as rf
    rf_daily = (1 + rf) ** (1 / Trading_days) - 1
    rf_quarterly = (1 + rf) ** (1 / 4) - 1
#now get market returns on daily and quarterly basis
#recall that market is the S&P 500 
    market_daily_arith = market.mean()  # daily arithmetic return
    market_quarterly_arith = market.mean() * Trading_days_quarter  # quarterly arithmetic


#now calculate daily and quarterly CAPM expected returns as we have all needed components:

    capm_er_daily = rf_daily + beta_cov * (market_daily_arith - rf_daily)
    capm_er_quarterly = rf_quarterly + beta_cov * (market_quarterly_arith - rf_quarterly)   

#caculate based on weights here
#pf_CAPM_ER_annual = capm_er_annual * eq weights.... etc

#Now display all results in streamlit

    st.write(f"Estimated Beta: {beta_cov:.4f}")
    st.write(f"Benchmark (S&P 500) Annual Return: {market_annual_arith:.2%}")
    st.write(f"CAPM Annual Expected Return for {tkr}: {capm_er_annual:.2%}")
    st.write(f"CAPM Quarterly Expected Return for {tkr}: {capm_er_quarterly:.2%}")
    st.write(f"CAPM Daily Expected Return for {tkr}: {capm_er_daily:.4%}")


   # Now calculate realized annual returns for the asset for comparison
   #use both arithmetic and geometric returns
    asset_clean = asset.dropna()
    realized_arith_pf = float(asset_clean.mean() * Trading_days) if len(asset_clean) > 0 else float("nan")
    realized_geom_pf = float((np.prod(1.0 + asset_clean) ** (Trading_days / len(asset_clean))) - 1.0) if len(asset_clean) > 0 else float("nan")

#create dataframe to hold results for display and download
    results_df = pd.DataFrame([{
        "Ticker": tkr,
        "Beta": beta_cov,
        "Benchmark (S&P 500) Annual Return": market_annual_arith,
        "CAPM Portfolio Annual Expected Return": capm_er_annual,
        "Annual Portfolio Arithmetic Return": realized_arith_pf,
        "Annual Portfolio Geometric Return": realized_geom_pf
    }]).set_index("Ticker")

    # UI choice between table and bar chart
    view = st.radio("Show", ["Table", "Bar Chart"], horizontal=True)

    if view == "Table":   # Table view using data frame
        st.dataframe(results_df.style.format({
            "Beta": "{:.4f}",
            "Benchmark (S&P 500) Annual Return": "{:.2%}",
            "CAPM Portfolio Annual Expected Return": "{:.2%}",
            "Annual Portfolio Arithmetic Return": "{:.2%}",
            "Annual Portfolio Geometric Return": "{:.2%}"
        }))
    else:  # Bar chart using plotly
        
        bar_df = pd.DataFrame({
            "Return Metric": ["CAPM Portfolio Annual Expected Return", "Annual Portfolio Arithmetic Return", "Annual Portfolio Geometric Return"],
            "Annual Percentage Return": [capm_er_annual, realized_geom_pf, realized_arith_pf]
        })
        fig = px.bar(bar_df, x="Return Metric", y="Annual Percentage Return", text=bar_df["Annual Percentage Return"].apply(lambda v: f"{v:.2%}"),
                     title= "CAPM vs Realized Annual Returns Chart")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    

#still to do:
#-----------------
# needs to be edited at top to account for multiple assets and not just one 
# create docstring at top explaining purpose of app and how to use it and what the variables are
# potentially change the capm code to be defined as one large function to make it easier to read
# could add in a histogram comparing daily returns distribution of portfolio vs S&P





 