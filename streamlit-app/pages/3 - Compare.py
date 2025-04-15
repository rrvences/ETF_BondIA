import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# Set the page configuration
st.set_page_config(
    page_title="BondIA Country Financial Data", 
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
            st.error(record["error"])
            return pd.DataFrame()  # Return an empty DataFrame on error
    else:
        st.error("Error fetching record from the server.")
        return pd.DataFrame()  # Return an empty DataFrame on error
    


    return pd.DataFrame([record])

# Streamlit app
st.title("Element Price Comparison")

# Load initial DataFrame (assuming you have a CSV or some data source)
# df = pd.read_csv('your_data.csv')  # Uncomment and modify this line to load your data
# For demonstration, let's create a sample DataFrame
list_of_isins = requests.get(f"{FASTAPI_URL}/json-records").json()

# Select box for elements
selected_elements = st.multiselect(
    "Select up to 4 elements to compare:",
    options=list_of_isins,
    max_selections=4
)

# If elements are selected, create a chart
if selected_elements:
    prices_df = pd.DataFrame()
    dividends_df = pd.DataFrame()
    info_df = pd.DataFrame()

    for element in selected_elements:
        # Assuming you have a way to get the ISIN for the element
        prices_df = pd.concat([prices_df, get_element_data_as_df(element, "etf_daily_prices")])
        info_df = pd.concat([info_df, get_element_data_as_df(element, "etf_info")])  # Assuming you want info

    # Create a bar chart using Plotly
    if not prices_df.empty:
        fig = go.Figure(data=[
            go.Bar(x=prices_df['isin'], y=prices_df['Close'], marker_color='skyblue')
        ])
        
        fig.update_layout(
            title='Price Comparison of Selected Elements',
            xaxis_title='Elements',
            yaxis_title='Price',
            template='plotly_white'
        )
        
        st.plotly_chart(fig)


    for element in selected_elements:
        st.dataframe(get_element_data_as_df(element, "etf_dividends_issued"))

    

    # Display profile info for selected elements
    #st.subheader("Profile Information")
    #for element in selected_elements:
    #    profile_info = info_df[info_df['isin'] == element]['Profile Info'].values[0]
    #    st.write(f"{element}: {profile_info}")

# Run the app
if __name__ == "__main__":
    st.write("Select elements to see their price comparison and profile information.")