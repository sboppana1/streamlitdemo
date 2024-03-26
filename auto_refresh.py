import streamlit as st
from datetime import datetime

def auto_refresh(interval_sec=300):
    # Injecting JavaScript for auto-refresh with the specified interval
    st.markdown(
        f"""
        <script>
        setTimeout(function() {{
            window.location.reload();
        }}, {interval_sec * 1000}); // Refreshes every {interval_sec} seconds
        </script>
        """,
        unsafe_allow_html=True,
    )

def main():
    st.title("Auto-Refresh Streamlit App")

    # Sidebar for user to specify refresh interval
    interval_sec = st.sidebar.number_input("Set Refresh Interval (seconds)", min_value=5, max_value=3600, value=5, step=5)
    
    # Display the current time to visualize the refresh behavior
    st.write("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Call the auto_refresh function with the user-specified interval
    auto_refresh(interval_sec)

if __name__ == "__main__":
    main()

