import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="My Stock Screener", layout="wide")

# 2. Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { 
        background-color: #1d4ed8; 
        color: white; 
        border-radius: 5px; 
        width: 100%; 
        font-weight: bold;
        height: 3em;
    }
    .stTextArea>div>div>textarea { 
        font-family: 'Courier New', monospace; 
        font-size: 16px; 
        border: 2px solid #cbd5e1; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data from your Google Sheet
# We set ttl=600 so it refreshes from your sheet every 10 minutes
@st.cache_data(ttl=600)
def load_data_from_google():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTISJa8GdWE749e4hzlQHYu2EKkPfdvkVco2BGg97Nzb02IgPCyIISmQPv2nxqjQYkNpCEb8mf9maBt/pub?gid=829168257&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        # CLEANING: Remove any accidental spaces in column names
        data.columns = data.columns.str.strip()
        # CLEANING: Remove NSE: or BOM: prefixes from Tickers for a cleaner look
        if 'Ticker' in data.columns:
            data['Ticker'] = data['Ticker'].astype(str).str.replace('NSE:', '').str.replace('BOM:', '')
        return data
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

df = load_data_from_google()

# 4. Sidebar info
st.sidebar.title("📊 Screener Stats")
if df is not None:
    st.sidebar.write(f"**Total Stocks in DB:** {len(df)}")
    st.sidebar.write("**Available Columns:**")
    for col in df.columns:
        st.sidebar.code(col)

# 5. Main UI
st.title("Custom Stock Search")
st.write("Enter your logic below. Use column names exactly as shown in the sidebar.")

# Query Input
default_query = "Market_Cap > 100000 and PE < 35"
query_text = st.text_area("Search Query", value=default_query, height=120)

if st.button("RUN QUERY"):
    if df is not None:
        try:
            # The Magic Query Engine
            results = df.query(query_text)
            
            st.subheader(f"Found {len(results)} results")
            
            # Display Table
            st.dataframe(
                results,
                use_container_width=True,
                column_config={
                    "Price": st.column_config.NumberColumn(format="₹%.2f"),
                    "Market_Cap": st.column_config.NumberColumn(format="%d Cr"),
                    "ROCE": st.column_config.NumberColumn(format="%.1f%%"),
                }
            )
            
            # CSV Download for the filtered results
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")
            
        except Exception as e:
            st.error(f"Logic Error: {e}")
            st.info("💡 Hint: Check your column names and make sure you use 'and' / 'or' (case sensitive in some versions).")

# 6. Data Preview
with st.expander("View Full Database (Raw Data)"):
    if df is not None:
        st.write(df)
