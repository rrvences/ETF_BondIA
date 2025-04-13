import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Set the page configuration
st.set_page_config(
    page_title="BondIA Country Financial Data", 
    page_icon="",      
    layout="wide"        
)

FASTAPI_URL = "http://fastapi-app:8000"


# Create DataFrames
credit_rates_df = pd.DataFrame(requests.get(f"{FASTAPI_URL}/country_list_ratings").json())
interest_rates_df = pd.DataFrame(requests.get(f"{FASTAPI_URL}/interest_rates").json())
debt_to_gdp_df = pd.DataFrame(requests.get(f"{FASTAPI_URL}/country_debt_to_gdp").json())
credit_rates_guide_df =pd.DataFrame(requests.get(f"{FASTAPI_URL}/credit_ratings_guide").json())


# Streamlit app
st.title("Country Financial Data")

# Create tabs for navigation
tab1, tab2, tab3 = st.tabs(["Credit Rates", "Interest Rates", "Debt to GDP"])

# Credit Rates Tab
with tab1:
    st.header("Country Credit Rates")
    st.dataframe(credit_rates_df)

    st.header("Credit Rates Guide")
    st.dataframe(credit_rates_guide_df)


# Interest Rates Tab
with tab2:
    st.header("Country Interest Rates")
    
    # Create a word map for credit rates
    fig = px.choropleth(debt_to_gdp_df,
                        locations="Country",
                        locationmode='country names',
                        color="Last",
                        hover_name="Country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Interest Rates by Country")

    st.plotly_chart(fig)
    st.dataframe(interest_rates_df)

# Debt to GDP Tab
with tab3:
    st.header("Country Debt to GDP")
    

    # Create a word map for credit rates
    fig = px.choropleth(debt_to_gdp_df,
                        locations="Country",
                        locationmode='country names',
                        color="Last",
                        hover_name="Country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Interest Rates by Country")
    
    st.plotly_chart(fig)
    st.dataframe(debt_to_gdp_df)