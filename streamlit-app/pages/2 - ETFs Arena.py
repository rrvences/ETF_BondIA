import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# Set the page configuration
st.set_page_config(
    page_title="BondIA ETFs Arena", 
    page_icon="",      
    layout="wide"        
)

FASTAPI_URL = "http://fastapi-app:8000"

def get_element_data_as_df(isin, element):
    # Call the FastAPI endpoint with a GET request
    response = requests.get(f"{FASTAPI_URL}/element?isin={isin}&element={element}")

    if response.status_code == 200:
        record = response.json()
    
        if "error" in record:
            return pd.DataFrame()  # Return an empty DataFrame on error
    
        else:
            return pd.DataFrame(record)
    
    else:
        st.error("Error fetching record from the server.")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Streamlit app
st.title("ETFs Price Comparison")


list_of_isins = requests.get(f"{FASTAPI_URL}/json-records").json()

# Select box for elements
selected_elements = st.multiselect(
    "Select up to 4 ETFs to compare:",
    options=list_of_isins,
    max_selections=4
)

# If elements are selected, create a chart
if selected_elements:
    all_prices_df = pd.DataFrame()
    all_info_df = pd.DataFrame()

fig = go.Figure()

for element in selected_elements:
    prices_df = get_element_data_as_df(element, "etf_daily_prices")
    #info_df = get_element_data_as_df(element, "etf_info")
    
    # Only add a line if both dataframes are not empty
    if not prices_df.empty:
        # Use the element name or ISIN as the label, adjust as needed
        fig.add_trace(
            go.Scatter(
                x=prices_df['date'],
                y=prices_df['Close'],
                mode='lines',
                name=element
            )
        )



# Only display the chart if at least one line was added
if fig.data:
    fig.update_layout(
        title='Price Comparison of Selected ETFs',
        xaxis_title='Date',
        yaxis_title='ETF Price',
        template='plotly_white',
        showlegend=True
    )
    st.plotly_chart(fig)


for element in selected_elements:
    dividends_df = get_element_data_as_df(element, "etf_dividends_issued")
    
    if dividends_df.empty:
        dividends_df = pd.DataFrame([{
            "ticker": "",
            "Dividends": "",
            "date": "",
            "isin": element
        }])
    
    st.info(f"Dividends Distributed by ISIN: {element}")
    st.dataframe(dividends_df)