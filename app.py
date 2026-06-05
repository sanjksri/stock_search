import streamlit as st
import pandas as pd
import yfinance as yf

# 1. Page Config
st.set_page_config(page_title="Stock Screener Clone", layout="wide")

# 2. Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Fetching with Fallback
@st.cache_data(ttl=3600)
def get_stock_data():
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ZOMATO.NS", 
               "TATAMOTORS.NS", "ITC.NS", "TITAN.NS", "SBIN.NS", "ADANIENT.NS"]
    
    all_data = []
    
    # Try to fetch live data
    try:
        with st.spinner('Attempting to fetch live market data...'):
            for t in tickers:
                stock = yf.Ticker(t)
                # We use a small timeout or check if info is valid
                info = stock.info
                if info and 'currentPrice' in info:
                    all_data.append({
                        'Ticker': t.replace(".NS", ""),
                        'Price': info.get('currentPrice'),
                        'PE': info.get('trailingPE'),
                        'Market_Cap': info.get('marketCap', 0) / 10000000,
                        'ROCE': info.get('returnOnCapitalEmployed', 15.0),
                        'Debt_to_Equity': info.get('debtToEquity', 0) / 100
                    })
    except Exception as e:
        print(f"Live fetch failed: {e}")

    # FALLBACK: If live data is empty (blocked by Yahoo), use high-quality Demo Data
    if not all_data:
        st.warning("⚠️ Live API is currently throttled. Loading cached/demo market data.")
        demo_data = [
            {'Ticker': 'RELIANCE', 'Price': 2950.0, 'PE': 28.5, 'Market_Cap': 1995000, 'ROCE': 12.5, 'Debt_to_Equity': 0.38},
            {'Ticker': 'TCS', 'Price': 4120.0, 'PE': 31.2, 'Market_Cap': 1485000, 'ROCE': 58.7, 'Debt_to_Equity': 0.02},
            {'Ticker': 'HDFCBANK', 'Price': 1510.0, 'PE': 17.8, 'Market_Cap': 1150000, 'ROCE': 16.5, 'Debt_to_Equity': 0.85},
            {'Ticker': 'INFY', 'Price': 1480.0, 'PE': 24.5, 'Market_Cap': 615000, 'ROCE': 40.2, 'Debt_to_Equity': 0.06},
            {'Ticker': 'ZOMATO', 'Price': 195.0, 'PE': 450.0, 'Market_Cap': 172000, 'ROCE': -1.2, 'Debt_to_Equity': 0.00},
            {'Ticker': 'TATAMOTORS', 'Price': 955.0, 'PE': 14.8, 'Market_Cap': 345000, 'ROCE': 18.2, 'Debt_to_Equity': 1.15},
            {'Ticker': 'ITC', 'Price': 430.0, 'PE': 26.1, 'Market_Cap': 540000, 'ROCE': 39.1, 'Debt_to_Equity': 0.00},
            {'Ticker': 'TITAN', 'Price': 3200.0, 'PE': 82.1, 'Market_Cap': 285000, 'ROCE': 25.4, 'Debt_to_Equity': 0.22}
        ]
        return pd.DataFrame(demo_data)
                
    return pd.DataFrame(all_data)

df = get_stock_data()

# 4. Sidebar Header
st.sidebar.title("🔍 Stock Screener")
st.sidebar.write("### Variables Available:")
st.sidebar.code("Price\nPE\nMarket_Cap\nROCE\nDebt_to_Equity")

# 5. Main UI
st.title("Search Query")
st.write("Find stocks using logic like: `Market_Cap > 500000 and PE < 35`")

query_input = st.text_area("Query box", value="Market_Cap > 100000 and ROCE > 15", height=120)

if st.button("RUN THIS QUERY"):
    try:
        results = df.query(query_input)
        st.subheader(f"Found {len(results)} results")
        st.dataframe(
            results.style.format({
                'Market_Cap': "{:,.0f} Cr",
                'Price': "₹{:,.2f}",
                'ROCE': "{:.1f}%",
                'PE': "{:.1f}"
            }),
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Query Error: {e}")

# 6. Full Data View
with st.expander("View All Available Data"):
    st.table(df)
