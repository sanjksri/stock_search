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
    .variable-tag {
        background-color: #e2e8f0;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85em;
        margin-right: 5px;
        border: 1px solid #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data from your Google Sheet
@st.cache_data(ttl=60) # Refreshes every 60 seconds
def load_data_from_google():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTISJa8GdWE749e4hzlQHYu2EKkPfdvkVco2BGg97Nzb02IgPCyIISmQPv2nxqjQYkNpCEb8mf9maBt/pub?gid=829168257&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        
        # --- DYNAMIC HEADER CLEANING ---
        # Strip spaces and replace spaces between words with underscores
        # This allows us to use them in df.query() safely
        data.columns = [c.strip().replace(' ', '_') for c in data.columns]
        
        # Automatically detect and convert ALL columns except Ticker to numbers
        for col in data.columns:
            if col != 'Ticker':
                # Convert to numeric, turn errors (like #N/A) into NaN
                data[col] = pd.to_numeric(data[col], errors='coerce')
                # Fill NaN (None) with 0 so the logic functions correctly
                data[col] = data[col].fillna(0)
        
        # Clean Ticker prefix if present
        if 'Ticker' in data.columns:
            data['Ticker'] = data['Ticker'].astype(str).str.replace('NSE:', '').str.replace('BOM:', '')
            
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data_from_google()

# 4. Sidebar info
st.sidebar.title("📊 Screener Stats")
if df is not None:
    st.sidebar.write(f"**Total Stocks:** {len(df)}")
    st.sidebar.write("**Available Columns:**")
    for col in df.columns:
        st.sidebar.code(col)

# 5. Main UI
st.title("Custom Stock Search")

if df is not None:
    # Show user the dynamic variable tags they can use
    st.write("### Available Query Variables")
    vars_html = "".join([f'<span class="variable-tag">{col}</span>' for col in df.columns])
    st.markdown(vars_html, unsafe_allow_html=True)
    st.write("")

    # Query Input - uses the first two dynamic columns as an example
    example_var = df.columns[1] if len(df.columns) > 1 else "Price"
    query_text = st.text_area("Search Query", value=f"{example_var} > 0", height=120)

    if st.button("RUN QUERY"):
        try:
            # The Magic Query Engine
            results = df.query(query_text)
            
            st.subheader(f"Found {len(results)} results")
            
            # --- DYNAMIC COLUMN FORMATTING ---
            # Automatically apply currency/percentage formats based on column names
            dynamic_config = {}
            for col in df.columns:
                if 'Price' in col:
                    dynamic_config[col] = st.column_config.NumberColumn(format="₹%.2f")
                elif 'Market_Cap' in col:
                    dynamic_config[col] = st.column_config.NumberColumn(format="%d Cr")
                elif 'ROCE' in col or 'Growth' in col:
                    dynamic_config[col] = st.column_config.NumberColumn(format="%.1f%%")
                elif df[col].dtype in ['float64', 'int64']:
                    dynamic_config[col] = st.column_config.NumberColumn(format="%.2f")

            st.dataframe(
                results,
                use_container_width=True,
                column_config=dynamic_config
            )
            
            # CSV Download
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")
            
        except Exception as e:
            st.error(f"Logic Error: {e}")
            st.info("💡 Hint: Use the column names exactly as shown in the gray tags above (e.g. use underscores for spaces).")

# 6. Data Preview
with st.expander("View Full Database (Raw Data)"):
    if df is not None:
        st.write(df)
