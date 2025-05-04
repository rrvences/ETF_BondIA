import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_utils import get_element_data_as_df, list_of_isins_available

# Set the page configuration
st.set_page_config(
    page_title="BondIA ETFs Arena", 
    page_icon="",      
    layout="wide"        
)


# Streamlit app
st.title("ETFs Price Comparison")

list_of_isins = list_of_isins_available()


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