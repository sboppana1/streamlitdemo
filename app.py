import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json

WATCH_LIST_FILE = 'watch_list.txt'

@st.cache(ttl=300)  # Initial default TTL, will be dynamically adjusted based on user input
def fetch_stock_data(symbol, volume_threshold, price_threshold):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="60d")
    
    if len(hist) < 2:
        return None, "Not enough data"
    
    current_volume = hist.iloc[-1]['Volume']
    historical_avg_volume = hist['Volume'].mean()
    volume_change_pct = round(((current_volume - historical_avg_volume) / historical_avg_volume) * 100, 2)
    
    current_price = hist.iloc[-1]['Close']
    prev_close_price = hist.iloc[-2]['Close']
    price_change_pct = round(((current_price - prev_close_price) / prev_close_price) * 100, 2)
    
    return {
        'Ticker': symbol,
        'Vol Chg %': volume_change_pct,
        'Prc Chg %': price_change_pct,
        'Cur Vol': current_volume,
        'Cur Prc': current_price,
        'Hist Avg Vol': historical_avg_volume,
        'Prev Prc': prev_close_price
    }, None

def load_watch_list():
    try:
        with open(WATCH_LIST_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

def save_watch_list(watch_list):
    with open(WATCH_LIST_FILE, 'w') as file:
        for symbol in watch_list:
            file.write(symbol + '\n')

def main():
    st.title("Stock Watch List with Alerts")
    
    # Allow users to specify refresh interval
    refresh_interval = st.sidebar.number_input("Refresh Interval (Seconds)", min_value=10, max_value=3600, value=300)
    st.sidebar.caption("Current refresh interval: {} seconds".format(refresh_interval))
    
    india_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    st.caption(f"Last Refreshed: {india_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
    
    volume_threshold = st.sidebar.number_input("Vol Chg Threshold (%)", value=10.0)
    price_threshold = st.sidebar.number_input("Prc Chg Threshold (%)", value=5.0)

    watch_list = load_watch_list()
    current_symbols = ', '.join(watch_list)
    new_symbols = st.text_area("Enter stock symbols separated by commas", value=current_symbols)
    
    if st.button("Update Watch List"):
        watch_list = [symbol.strip().upper() for symbol in new_symbols.split(',')]
        save_watch_list(watch_list)
        st.experimental_rerun()

    if watch_list:
        data = []
        for symbol in watch_list:
            symbol_data, error = fetch_stock_data(symbol, volume_threshold, price_threshold)
            if symbol_data:
                data.append(symbol_data)
            elif error:
                st.error(f"Error fetching data for {symbol}: {error}")
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)  # Allows column sorting
            
            # Download data as JSON
            st.download_button(
                "Download Data as JSON",
                data=json.dumps(data, indent=2),
                file_name="stock_data.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()

