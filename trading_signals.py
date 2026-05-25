import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from benzinga import financial_data
import os

st.set_page_config(page_title="My Trading Signals", layout="wide")
st.title("🚀 My Personal Trading Signals (24/7)")

# Get API key from Railway (secure way)
BENZINGA_API_KEY = os.environ.get("BENZINGA_API_KEY", "")

if not BENZINGA_API_KEY:
    st.error("Please add your Benzinga API key in Railway Variables!")
    st.stop()

# Simple sidebar
ticker = st.text_input("Enter Ticker", value="SPY").upper()

if st.button("Get Live Signal", type="primary"):
    with st.spinner("Fetching data..."):
        try:
            bz = financial_data.Benzinga(BENZINGA_API_KEY)
            quote = bz.delayed_quote(company_tickers=ticker)
            price = float(quote['data'][0]['last_trade_price'])
            st.metric("Current Price", f"${price:,.2f}")
            
            # Simple signal
            data = yf.download(ticker, period="3d", interval="5m", progress=False)
            if not data.empty:
                last_close = float(data['Close'].iloc[-1])
                if price > last_close * 1.008:
                    st.success("**BUY** - Price is rising")
                elif price < last_close * 0.992:
                    st.error("**SELL** - Price is falling")
                else:
                    st.info("**HOLD** - No strong move")
        except Exception as e:
            st.error(f"Error: {str(e)}")