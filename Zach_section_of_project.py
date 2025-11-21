
#displaying company name in streamlit app 
tkr_obj = yf.Ticker(ticker)
try:
        ticker_info = tkr_obj.info 
except Exception:
        ticker_info = {} #handle case where no info available
        
company_name = (ticker_info.get("longName") or ticker_info.get("shortName") or tkr) # get companies full name or short name depending on what is available in database

if ticker_info:
        st.write(f"Company Name: {company_name}")
else:
        st.write("Company Name: Not Found")

#links to latest news regarding most recently added ticker to the portfolio
ft_query = company_name.replace(" ", "+")  # in order to correctly handle the URL
ft_search = f"https://www.ft.com/search?q={ft_query}"
st.caption(f"For the latest news from the Financial Times on {company_name}")
st.write(f"[Click here]({ft_search})")
st.caption(f"Note that no new articles may be available for the chosen stock.")

# ensure ticker_returns and SPX_returns are Series (handles DataFrame from yfinance)
ticker_returns = tkr_data.pct_change().dropna()
SPX_returns = bm_data.pct_change().dropna()
#I have a simpler version also but this is needed in order to have sliders in the current 

if isinstance(ticker_returns, pd.DataFrame):
    ticker_returns = ticker_returns.iloc[:, 0].squeeze()
else:
    ticker_returns = ticker_returns.squeeze()

if isinstance(SPX_returns, pd.DataFrame):
    SPX_returns = SPX_returns.iloc[:, 0].squeeze()
else:
    SPX_returns = SPX_returns.squeeze()

# interactive sliders and moving average plots (only when data exists)
if ticker_returns.empty or SPX_returns.empty:
    st.warning("Not enough data to display interactive return charts.")
else:
    # choosing window based on overlapping length so both series have values
    n_max = max(1, min(len(ticker_returns), len(SPX_returns)))
    show_days = st.slider("Show Last N Days", min_value=1, max_value=365, value= 365)
    ma_window = st.slider("Moving Average Length (Days)", min_value=0, max_value=60, value=0)

    # take tail of each series and align by date
    pf_display = ticker_returns.tail(show_days)
    bm_display = SPX_returns.tail(show_days)
    df_plot = pd.concat([pf_display.rename(ticker), bm_display.rename("S&P500")], axis=1).dropna()

    # add moving averages if requested and creating a dataframe for plotting and drop NaNs to avoid errors
    if ma_window > 0:
        df_plot[f"{ticker}_MA"] = df_plot[ticker].rolling(window=ma_window).mean()
        df_plot["S&P500_MA"] = df_plot["S&P500"].rolling(window=ma_window).mean()

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

        st.caption("Data period: 5 years (Adjusted Close)")

# CAPM expected return calculations
Trading_days = 252 # assuming 252 trading days in a year

#add in section subheader into streamlit app
st.subheader("CAPM Model")
st.caption("CAPM Formula: E(Ri) = Rf + βi (E(Rm) - Rf)")

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

    # Calculate beta -> done earlier by michael


    # Get market rate first to get market risk premium
    market_annual_arith = market.mean() * Trading_days

    # CAPM expected return formula is risk free rate + beta * (market return - risk free rate)
    capm_er_annual = rf + Beta * (market_annual_arith - rf)

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

    capm_er_daily = rf_daily + Beta * (market_daily_arith - rf_daily)
    capm_er_quarterly = rf_quarterly + Beta * (market_quarterly_arith - rf_quarterly)   

    cols = st.columns(5)
    cols[0].metric("Beta", f"{Beta:.4f}")
    cols[1].metric("S&P 500 Annual return", f"{market_annual_arith:.2%}")
    cols[2].metric("CAPM Annual Return", f"{capm_er_annual:.2%}")
    cols[3].metric("CAPM Quarterly Return", f"{capm_er_quarterly:.2%}")
    cols[4].metric("CAPM Daily Return", f"{capm_er_daily:.4%}")


    # Now calculate realized annual returns for the asset for comparison
    #use both arithmetic and geometric returns
    asset_clean = asset.dropna()
    realized_arith_pf = float(asset_clean.mean() * Trading_days) if len(asset_clean) > 0 else float("nan")
    realized_geom_pf = float((np.prod(1.0 + asset_clean) ** (Trading_days / len(asset_clean))) - 1.0) if len(asset_clean) > 0 else float("nan")

    #create dataframe to hold results for display and download
    results_df = pd.DataFrame([{
    "Ticker": ticker,
    "Beta": Beta,
    "S&P 500 Annual Return": market_annual_arith,
    "CAPM Annual Expected Return": capm_er_annual,
    "Arithmetic Annual Expected Return": realized_arith_pf,
    "Geometric Annual Expected Return": realized_geom_pf
    }]).set_index("Ticker")

    # UI choice between table and bar chart
    view = st.radio("Show", ["Table", "Bar Chart"], horizontal=True)


    # UI choice: show Bar Chart first, then Table
    view = st.radio("Show", ["Bar Chart", "Table"], index=0, horizontal=True)

    if view == "Bar Chart":
        bar_df = pd.DataFrame({
            "Return Metric": ["CAPM Annual Expected Return", "Arithmetic Annual Expected Return", "Geometric Annual Expected Return"],
            "Annual Percentage Return": [capm_er_annual, realized_geom_pf, realized_arith_pf]
        })
        fig = px.bar(bar_df, x="Return Metric", y="Annual Percentage Return",
                     text=bar_df["Annual Percentage Return"].apply(lambda v: f"{v:.2%}"),
                     title="CAPM vs Realized Annual Returns Chart")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
    else:  # Table
        st.dataframe(results_df.style.format({
            "Beta": "{:.4f}",
            "Benchmark (S&P 500) Annual Return": "{:.2%}",
            "CAPM Annual Expected Return": "{:.2%}",
            "Arithmetic Annual Expected Return": "{:.2%}",
            "Geometric Annual Expected Return": "{:.2%}"
        }))











# %%
