#%%
#importing libraries and creating environment
import yfinance as yf
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st #use for dashboard launching

#--------------------------------------------------------------------------#

#getting stock data for chosen portfolio from yfinance
tkr = st.text_input("Enter Stock Ticker", "AAPL").upper() #uppercase tickers to match yfinance format
tkr_data = yf.download([tkr], period = '1y', auto_adjust= True)

#obtaining data from benchmark index (S&P 500)
bm_data = yf.download(["^GSPC"], period = '1y', auto_adjust= True)

#calculating daily returns for both portfolio and benchmark
# portfolio daily returns first:
pf_returns = tkr_data['Close'].pct_change().dropna() 

# benchmark daily returns next:
bm_returns = bm_data['Close'].pct_change().dropna()

#print results to console for verification
print(pf_returns)
print(bm_returns)

# Display results in Streamlit app

# ensure pf_returns and bm_returns are Series (handles DataFrame from yfinance)
#I have a simpler version also but this is needed in order to have sliders in the current version
if isinstance(pf_returns, pd.DataFrame):
    pf_returns = pf_returns.iloc[:, 0].squeeze()
else:
    pf_returns = pf_returns.squeeze()

if isinstance(bm_returns, pd.DataFrame):
    bm_returns = bm_returns.iloc[:, 0].squeeze()
else:
    bm_returns = bm_returns.squeeze()

# interactive sliders and moving average plots (only when data exists)
if pf_returns.empty or bm_returns.empty:
    st.warning("Not enough data to display interactive return charts.")
else:
    # choosing window based on overlapping length so both series have values
    n_max = max(1, min(len(pf_returns), len(bm_returns)))
    show_days = st.slider("Show Last N Days", min_value=1, max_value=n_max, value=min(90, n_max))
    ma_window = st.slider("Moving Average Length (Days)", min_value=0, max_value=60, value=0)

    # take tail of each series and align by date
    pf_display = pf_returns.tail(show_days)
    bm_display = bm_returns.tail(show_days)
    df_plot = pd.concat([pf_display.rename(tkr), bm_display.rename("S&P500")], axis=1).dropna()

    # add moving averages if requested
    if ma_window > 0:
        df_plot[f"{tkr}_MA"] = df_plot[tkr].rolling(window=ma_window).mean()
        df_plot["S&P500_MA"] = df_plot["S&P500"].rolling(window=ma_window).mean()

    # portfolio chart
    st.write(f"Daily Returns for {tkr} (last {show_days} days):")
    if ma_window > 0:
        st.line_chart(df_plot[[tkr, f"{tkr}_MA"]])
    else:
        st.line_chart(df_plot[[tkr]])

    # benchmark chart
    st.write("Daily Returns for Benchmark (S&P 500):")
    if ma_window > 0:
        st.line_chart(df_plot[["S&P500", "S&P500_MA"]])
    else:
        st.line_chart(df_plot[["S&P500"]])
  


# %% CAPM expected return calculation
Trading_days = 252 # assuming 252 trading days in a year

# allow user to set risk-free rate (annual, decimal)
#risk free rate is defaulted to 2% but user can change it betwween 0% and 4%
rf = st.number_input("Choose Annual Risk-Free Rate (Default = 2%)", min_value=0.0, max_value= 0.04, value=0.02, step=0.001, format="%.4f")

   

# align asset and market returns on overlapping dates
combined = pd.concat([pf_returns, bm_returns], axis=1).dropna()
combined.columns = ['asset', 'market']

if combined.empty:
    st.warning("Not enough overlapping returns to compute CAPM. Check data/period.")
else:
    asset = combined['asset']
    market = combined['market']

    # Calculate beta as covariance(asset, market) / variance(market)
    beta_cov = np.cov(asset, market)[0, 1] / np.var(market)
    

    # Have market annual arithmetic return for comparison
    # code for CAGR can be added later if needed
    market_annual_arith = market.mean() * Trading_days

    # CAPM expected return (annual)
    capm_er = rf + beta_cov * (market_annual_arith - rf)

    # Display results in streamlit app
    # beta display is maybe unnecessary but it is useful to see
    st.subheader("CAPM Results")
    st.write(f"Estimated Beta (Cov/Var): {beta_cov:.4f}")
    st.write(f"Market Annual Return (Arithmetic): {market_annual_arith:.2%}")
    st.write(f"CAPM Expected Annual Return for {tkr}: {capm_er:.2%}")

   
    asset_clean = asset.dropna()
    realized_arith = float(asset_clean.mean() * Trading_days) if len(asset_clean) > 0 else float("nan")
    realized_geom = float((np.prod(1.0 + asset_clean) ** (Trading_days / len(asset_clean))) - 1.0) if len(asset_clean) > 0 else float("nan")

    results_df = pd.DataFrame([{
        "Ticker": tkr,
        "Beta": beta_cov,
        "Market Annual Arithmetic Return": market_annual_arith,
        "CAPM Expected Return": capm_er,
        "Realized Arithmetic Return": realized_arith,
        "Realized Geometric Return": realized_geom
    }]).set_index("Ticker")

    # UI choice between table and bar chart
    view = st.radio("Show", ["Table", "Bar chart"], horizontal=True)

    if view == "Table":   # Table view
        st.dataframe(results_df.style.format({
            "Beta": "{:.4f}",
            "Market Annual Arithmetic Return": "{:.2%}",
            "CAPM Expected Return": "{:.2%}",
            "Realized Arithmetic Return": "{:.2%}",
            "Realized Geometric Return": "{:.2%}"
        }))
    else:  # Bar chart
        import plotly.express as px
        bar_df = pd.DataFrame({
            "Measure": ["CAPM Expected", "Realized (Geom)", "Realized (Arith)"],
            "Value": [capm_er, realized_geom, realized_arith]
        })
        fig = px.bar(bar_df, x="Measure", y="Value", text=bar_df["Value"].apply(lambda v: f"{v:.2%}"),
                     title=f"{tkr}: CAPM vs Realized Annual Returns")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    # Download results as CSV option (probably not needed for single asset but useful for multiple)
    csv = results_df.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("Download CAPM Summary CSV", data=csv, file_name=f"{tkr}_capm_summary.csv", mime="text/csv")
    

# needs to be edited at top to account for multiple assets and not just one 
# need to code for a dashboard slide 
# add in code for equal weighted portfolio calculations
# would like to change colours and layout of dashboard also

