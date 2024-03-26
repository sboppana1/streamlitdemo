import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

WATCH_LIST_FILE = 'watch_list.txt'

def fetch_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        if len(hist) < 2:
            return {"Ticker": symbol, "Error": "Not enough data"}
        
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
        }
    except Exception as e:
        return {"Ticker": symbol, "Error": str(e)}

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
    
    refresh_interval = st.sidebar.number_input("Refresh Interval (Seconds)", value=30, min_value=5, max_value=3600)
    
    if 'next_refresh' not in st.session_state or datetime.now() >= st.session_state['next_refresh']:
        st.session_state['next_refresh'] = datetime.now() + timedelta(seconds=refresh_interval)
        st.session_state['last_refreshed'] = datetime.now(pytz.timezone('Asia/Kolkata'))
    
    watch_list = load_watch_list()
    current_symbols = ', '.join(watch_list)
    new_symbols = st.text_area("Enter stock symbols separated by commas", value=current_symbols)
    
    if st.button("Update Watch List"):
        watch_list = [symbol.strip().upper() for symbol in new_symbols.split(',')]
        save_watch_list(watch_list)
        st.session_state['next_refresh'] = datetime.now()  # Force refresh
        st.session_state['last_refreshed'] = datetime.now(pytz.timezone('Asia/Kolkata'))

    data = [fetch_stock_data(symbol) for symbol in watch_list if symbol]
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)  # Make table columns sortable and use maximum width

    # Display the last refreshed time
    last_refreshed_time = st.session_state.get('last_refreshed', datetime.now(pytz.timezone('Asia/Kolkata')))
    st.caption(f"Last Refreshed: {last_refreshed_time.strftime('%Y-%m-%d %H:%M:%S IST')}")

    if datetime.now() >= st.session_state['next_refresh']:
        st.experimental_rerun()

if __name__ == "__main__":
    main()

