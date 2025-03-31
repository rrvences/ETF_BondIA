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
    
    return record["element"]


# Button to fetch the maturity record
if compare_button:

    table_maturity_1 = get_element_data(isin1,"maturity")
    table_maturity_2 = get_element_data(isin2,"maturity")

        # Convert to DataFrame
    df1 = pd.DataFrame(list(table_maturity_1.items()), columns=['Maturity', 'Value 1'])
    df2 = pd.DataFrame(list(table_maturity_2.items()), columns=['Maturity', 'Value 2'])

    # Convert values to numeric
    df1['Value 1'] = df1['Value 1'].replace('%', '', regex=True).astype(float)
    df2['Value 2'] = df2['Value 2'].replace('%', '', regex=True).astype(float)

    # Streamlit App
    st.title("Maturity Tables Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Table Maturity 1")
        st.dataframe(df1)
    with col2:
        st.write("### Table Maturity 2")
        st.dataframe(df2)

    # Merging Data for Comparison
    df_merged = pd.merge(df1, df2, on='Maturity', how='outer').fillna(0)

    # Plot Comparison
    st.write("### Maturity Distribution Comparison")
    fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
                x='Maturity', y='Percentage', color='Table', barmode='group',
                title="Comparison of Maturity Distributions")
    st.plotly_chart(fig)
