import streamlit as st
import pandas as pd
import yfinance as yf

# Page Config
st.set_page_config(page_title="Stock Screener Clone", layout="wide")

# 1. Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { background-color: #1d4ed8; color: white; width: 100%; border-radius: 5px; font-weight: bold; }
    .stTextArea>div>div>textarea { font-family: monospace; border: 1px solid #ccd1d9; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Fetching Logic
@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_stock_data():
    # List of Indian Tickers (Add more as needed)
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ZOMATO.NS", 
               "TATAMOTORS.NS", "ITC.NS", "TITAN.NS", "SBIN.NS", "ADANIENT.NS"]
    
    all_data = []
    
    # Progress bar because fetching live data takes time
    with st.spinner('Fetching live market data...'):
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                info = stock.info
                all_data.append({
                    'Ticker': t.replace(".NS", ""),
                    'Price': info.get('currentPrice'),
                    'PE': info.get('trailingPE'),
                    'Market_Cap': info.get('marketCap', 0) / 10000000, # Convert to Crores
                    'ROCE': info.get('returnOnCapitalEmployed', 15.5), # Fallback value if null
                    'Debt_to_Equity': info.get('debtToEquity', 0) / 100 # Normalize
                })
            except Exception:
                continue # Skip stocks that fail to fetch
                
    return pd.DataFrame(all_data)

# FIX: Calling the correctly named function
df = get_stock_data()

# 3. Sidebar Header
st.sidebar.title("🔍 Stock Screener")
st.sidebar.info("""
**Variables available:**
- `Price`
- `Market_Cap` (in Cr)
- `PE`
- `ROCE`
- `Debt_to_Equity`
""")

# 4. Main UI
st.title("Create a search query")
st.write("Write your logic below (e.g., `Market_Cap > 100000 and PE < 30`)")

# Default query
query_input = st.text_area("Query box", value="Market_Cap > 50000 and PE < 40", height=120)

if st.button("RUN THIS QUERY"):
    if df.empty:
        st.error("No data available. Check your internet connection or ticker list.")
    else:
        try:
            # The Magic Logic: Pandas query handles 'and/or' automatically
            filtered_df = df.query(query_input)
            
            st.subheader(f"Found {len(filtered_df)} results")
            
            # Display table with formatting
            # Note: We use try/except on formatting in case some columns are missing
            st.dataframe(
                filtered_df.style.format({
                    'Market_Cap': "{:,.0f} Cr",
                    'Price': "₹{:,.2f}",
                    'ROCE': "{:.1f}%",
                    'PE': "{:.1f}",
                    'Debt_to_Equity': "{:.2f}"
                }),
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error in query logic: {e}")
            st.info("Check if you typed column names correctly (case sensitive).")

# 5. Export Feature
if not df.empty:
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download All Data as CSV",
        data=csv,
        file_name="screener_data.csv",
        mime="text/csv",
    )
