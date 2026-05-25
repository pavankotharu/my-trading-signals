import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import os

st.set_page_config(page_title="My Trading Signals", layout="wide")
st.title("🚀 My Personal Trading Signals (24/7)")

# Get Telegram credentials from Railway
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ticker = st.text_input("Enter Ticker", value="SPY").upper()

if st.button("Get Live Signal", type="primary"):
    with st.spinner("Analyzing..."):
        try:
            data = yf.download(ticker, period="5d", interval="5m", progress=False)
            
            if data.empty:
                st.error("Could not fetch data. Try again.")
            else:
                df = data.copy()
                df['rsi'] = ta_rsi(df['Close'])
                df['macd'], df['macd_signal'] = ta_macd(df['Close'])
                df['vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
                
                last = df.iloc[-1]
                price = float(last['Close'])
                
                score = 50
                reasons = []
                
                if price > last['vwap']:
                    score += 15
                    reasons.append("Above VWAP")
                if last['rsi'] < 35:
                    score += 20
                    reasons.append("Oversold RSI")
                if last['macd'] > last['macd_signal']:
                    score += 15
                    reasons.append("MACD Bullish")
                
                if score >= 75:
                    signal = "STRONG BUY"
                    st.success(f"**{signal}** - Confidence: {score}%")
                elif score >= 60:
                    signal = "BUY"
                    st.success(f"**{signal}** - Confidence: {score}%")
                elif score <= 25:
                    signal = "STRONG SELL"
                    st.error(f"**{signal}** - Confidence: {score}%")
                elif score <= 40:
                    signal = "SELL"
                    st.error(f"**{signal}** - Confidence: {score}%")
                else:
                    signal = "HOLD"
                    st.info(f"**{signal}** - Confidence: {score}%")
                
                st.write(f"**Current Price:** ${price:.2f}")
                
                # Send Telegram alert
                if "STRONG" in signal and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                    msg = f"🚨 {signal} on {ticker}\nPrice: ${price:.2f}\nConfidence: {score}%"
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
                    st.success("✅ Telegram alert sent!")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")

def ta_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ta_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line    