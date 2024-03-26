import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json

WATCH_LIST_FILE = 'watch_list.txt'

def fetch_data(symbol, volume_threshold, price_threshold):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="60d")
    
    if len(hist) < 2:
        return None, "Not enough data"
    
    current_volume = hist.iloc[-1]['Volume']
    historical_avg_volume = hist['Volume'].mean()
    volume_change_pct = ((current_volume - historical_avg_volume) / historical_avg_volume) * 100
    
    current_price = hist.iloc[-1]['Close']
    prev_close_price = hist.iloc[-2]['Close']
    price_change_pct = ((current_price - prev_close_price) / prev_close_price) * 100
    
    alerts = []
    if abs(volume_change_pct) > volume_threshold:
        alerts.append(f"Volume change ({volume_change_pct:.2f}%) exceeds threshold.")
    if abs(price_change_pct) > price_threshold:
        alerts.append(f"Price change ({price_change_pct:.2f}%) exceeds threshold.")
    
    return {
        'Symbol': symbol,
        'Current Volume': current_volume,
        'Historical Avg Volume': historical_avg_volume,
        'Volume Change %': volume_change_pct,
        'Current Price': current_price,
        'Prev Close Price': prev_close_price,
        'Price Change %': price_change_pct,
        'Alerts': alerts
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

    # Displaying the Indian timestamp of last refresh
    india_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    st.caption(f"Last Refreshed: {india_time.strftime('%Y-%m-%d %H:%M:%S IST')}")

    volume_threshold = st.sidebar.number_input("Volume Change Threshold (%)", value=10.0)
    price_threshold = st.sidebar.number_input("Price Change Threshold (%)", value=5.0)

    watch_list = load_watch_list()
    
    # Display the currently configured watch list symbols in the textbox
    current_symbols = ', '.join(watch_list)
    new_symbols = st.text_area("Enter stock symbols separated by comma (e.g., AAPL, MSFT, GOOGL)", value=current_symbols)
    if st.button("Update Watch List"):
        watch_list = [symbol.strip().upper() for symbol in new_symbols.split(',')]
        save_watch_list(watch_list)
        st.experimental_rerun()

    if watch_list:
        data = []
        for symbol in watch_list:
            symbol_data, error = fetch_data(symbol, volume_threshold, price_threshold)
            if symbol_data:
                data.append(symbol_data)
            elif error:
                st.error(f"Error fetching data for {symbol}: {error}")
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, width=700, height=400)
            
            # Download button for JSON data
            st.download_button(
                label="Download Data as JSON",
                data=json.dumps(data, indent=2),
                file_name='stocks_data.json',
                mime='application/json'
            )

if __name__ == "__main__":
    main()

