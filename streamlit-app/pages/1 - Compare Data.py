import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="BondIA Comparator", 
    page_icon="⚔️",      
    layout="wide"        
)

st.title("Compare ETF BondIA")

FASTAPI_URL = "http://fastapi-app:8000"

# Create a sidebar for the app
sidebar = st.sidebar

list_of_isins = requests.get(f"{FASTAPI_URL}/json-records").json()

isin1 = sidebar.selectbox('Isin1',list_of_isins)
isin2 = sidebar.selectbox('Isin2',list_of_isins)
compare_button = sidebar.button('Compare')


def get_element_data(isin,element):
     # Call the FastAPI endpoint with a GET request
    response = requests.get(f"{FASTAPI_URL}/element?isin={isin}&element={element}")

    if response.status_code == 200:
            record = response.json()
            if "error" in record:
                st.error(record["error"])
    else:
        st.error("Error fetching record from the server.")
    
    return record[element]


def merge_tables(tables, element):

    tables_df = [pd.DataFrame(list(tables[isin].items()), columns=[element, isin]) for isin in tables.keys()]
    return pd.concat(tables_df)

all_isin = [isin1, isin2]

# Button to fetch the maturity record
if compare_button:

    tables_maturity = {}
    tables_rating = {}
    tables_market = {}
    tables_portfolio = {}
    
    for isin in all_isin:
        tables_maturity[isin] = get_element_data(isin, "maturity")
        tables_rating[isin] = get_element_data(isin, "credit_rate")
        tables_market[isin] = get_element_data(isin, "market_allocation")
        tables_portfolio[isin] = get_element_data(isin, "portfolio")

    df_merged = merge_tables(tables_portfolio, element='Portfolio')
    st.dataframe(df_merged)
    
    # Maturity
    df_merged = merge_tables(tables_maturity, element='Maturity')
    # Plot Comparison
    st.write("### Maturity Distribution Comparison")
    fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
                x='Maturity', y='Percentage', color='Table', barmode='group',
                title="Comparison of Maturity Distributions")
    st.plotly_chart(fig)


    ### RATING
    df_merged = merge_tables(tables_rating, element='Rating')
    # Plot Rating Breakdown
    st.write("### Rating Breakdown Comparison")
    fig_rating = px.bar(df_merged.melt(id_vars=['Rating'], var_name='Table', value_name='Percentage'), 
                        x='Rating', y='Percentage', color='Table', barmode='group',
                        title="Comparison of Rating Breakdown")

    fig_rating.update_layout(barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    st.plotly_chart(fig_rating)

    ### MARKET ALLOCATION
    # Standardizing Country Names (Removing extra words for consistency)

    df_merged = merge_tables(tables_market, element='Country')
    # Plot
    st.write("### Market Allocation Comparison")
    fig_market = px.bar(df_merged.melt(id_vars=['Country'], var_name='Table', value_name='Percentage'),
                        y='Country', x='Percentage', color='Table', barmode='group',
                        title="Comparison of Market Allocation",
                        orientation='h')  # Horizontal bars

    