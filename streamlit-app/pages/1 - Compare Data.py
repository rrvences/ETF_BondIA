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


def clean_tables(table_1, table_2, element):

        # Convert to DataFrame
        df1 = pd.DataFrame(list(table_1.items()), columns=[element, 'Value 1'])
        df2 = pd.DataFrame(list(table_2.items()), columns=[element, 'Value 2'])

        # Convert values to numeric
        df1['Value 1'] = df1['Value 1'].replace('%', '', regex=True).astype(float)
        df2['Value 2'] = df2['Value 2'].replace('%', '', regex=True).astype(float)

        df_merged = pd.merge(df1, df2, on=element, how='outer').fillna(0)
        return df1, df2, df_merged


def clean_keys(table):
    table = {key.split(" ")[0].capitalize(): value for key, value in table.items() 
             if "Total" not in key and 'Derivatives' not in key}

    return table

# Button to fetch the maturity record
if compare_button:

    table_maturity_1 = get_element_data(isin1,"maturity")
    table_maturity_2 = get_element_data(isin2,"maturity")


    table_rating_1 = get_element_data(isin1,"credit_rate")
    table_rating_2 = get_element_data(isin2,"credit_rate")

    
    table_market_1 = get_element_data(isin1,"market_allocation")
    table_market_2 = get_element_data(isin2,"market_allocation")


    # Maturity
    df1, df2, df_merged = clean_tables(clean_keys(table_maturity_1), clean_keys(table_maturity_2), element='Maturity')
    # Plot Comparison
    st.write("### Maturity Distribution Comparison")
    fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
                x='Maturity', y='Percentage', color='Table', barmode='group',
                title="Comparison of Maturity Distributions")
    st.plotly_chart(fig)


    ### RATING
    df1, df2, df_merged = clean_tables(clean_keys(table_rating_1), clean_keys(table_rating_2), element='Rating')

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

    df1, df2, df_market_merged = clean_tables(clean_keys(table_market_1), clean_keys(table_market_2), element='Country')
    # Sort by first dataset for better comparison
    df_market_merged = df_market_merged.sort_values(by="Value 1", ascending=False)

    # Plot
    st.write("### Market Allocation Comparison")
    fig_market = px.bar(df_market_merged.melt(id_vars=['Country'], var_name='Table', value_name='Percentage'),
                        y='Country', x='Percentage', color='Table', barmode='group',
                        title="Comparison of Market Allocation",
                        orientation='h')  # Horizontal bars

    st.plotly_chart(fig_market)