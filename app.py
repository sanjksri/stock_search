import streamlit as st
import pandas as pd
import yfinance as yf

# Page Config
st.set_page_config(page_title="Stock Screener Clone", layout="wide")

# 1. Custom Styling (Screener.in look)
# Change "unsafe_allow_now" to "unsafe_allow_html"
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { background-color: #1d4ed8; color: white; width: 100%; }
    .stTextArea>div>div>textarea { font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)
# 2. Mock Data / API Integration
@st.cache_data
def get_stock_data():
    # In a real app, you would fetch this from an API or Database
    # Here we create a sample dataset for demonstration
    data = {
        'Ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ZOMATO', 'TATAMOTORS', 'ITC', 'TITAN'],
        'Price': [2950, 4120, 1510, 1480, 195, 955, 430, 3200],
        'Market_Cap': [1900000, 1400000, 1100000, 600000, 170000, 340000, 540000, 280000],
        'PE': [28.5, 31.2, 17.8, 24.5, 480, 14.8, 26.1, 82.1],
        'ROCE': [12.5, 58.7, 16.5, 40.2, -1.2, 18.2, 39.1, 25.4],
        'Debt_to_Equity': [0.38, 0.02, 0.85, 0.06, 0.00, 1.15, 0.00, 0.22]
    }
    return pd.DataFrame(data)

df = get_stock_data()

# 3. Sidebar Header
st.sidebar.title("🔍 Stock Screener")
st.sidebar.info("Variables: `Price`, `Market_Cap`, `PE`, `ROCE`, `Debt_to_Equity`")

# 4. Main UI
st.title("Create a search query")
query = st.text_area("Query box", value="Market_Cap > 500000 and PE < 30", height=150)

if st.button("RUN THIS QUERY"):
    try:
        # The Magic Logic
        filtered_df = df.query(query)
        
        st.subheader(f"Found {len(filtered_df)} results")
        
        # Display table with formatting
        st.dataframe(
            filtered_df.style.format({
                'Market_Cap': "{:,.0f}",
                'Price': "₹{:,.2f}",
                'ROCE': "{:.1f}%"
            }).highlight_max(axis=0, subset=['ROCE'], color='#dcfce7'),
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error in query logic: {e}")
        st.info("Example query: Market_Cap > 100000 and ROCE > 15")

# 5. Export Feature
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Export to CSV", data=csv, file_name="screen_results.csv", mime="text/csv")
