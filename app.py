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
def get_live_data(tickers):
    # Fetch data for a list of tickers
    all_data = []
    for t in tickers:
        stock = yf.Ticker(t)
        info = stock.info
        all_data.append({
            'Ticker': t,
            'Price': info.get('currentPrice'),
            'PE': info.get('trailingPE'),
            'Market_Cap': info.get('marketCap')
        })
    return pd.DataFrame(all_data)

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
