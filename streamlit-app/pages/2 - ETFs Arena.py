import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# Set the page configuration
st.set_page_config(
    page_title="BondIA ETFs Arena", 
    page_icon="",      
    layout="wide"        
)

FASTAPI_URL = "http://fastapi-app:8000"

def get_etf_element_data_as_df(isin, element):
    # Call the FastAPI endpoint with a GET request
    response = requests.get(f"{FASTAPI_URL}/element?isin={isin}&element={element}")

    if response.status_code == 200:
        record = response.json()
    
        if not record:
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
selected_etfs = st.multiselect(
    "Select up to 4 ETFs to compare:",
    options=list_of_isins,
    max_selections=4
)

# If elements are selected, create a chart
if selected_etfs:
    all_prices_df = pd.DataFrame()
    all_info_df = pd.DataFrame()

fig = go.Figure()

for isin in selected_etfs:
    prices_df = get_etf_element_data_as_df(isin, "etf_daily_prices")
    #info_df = get_element_data_as_df(element, "etf_info")
    
    # Only add a line if both dataframes are not empty
    if not prices_df.empty:
        # Use the element name or ISIN as the label, adjust as needed
        fig.add_trace(
            go.Scatter(
                x=prices_df['date'],
                y=prices_df['Close'],
                mode='lines',
                name=isin
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


for isin in selected_etfs:
    dividends_df = get_etf_element_data_as_df(isin, "etf_dividends_issued")
    
    if dividends_df.empty:
        dividends_df = pd.DataFrame([{
            "ticker": "",
            "Dividends": "",
            "date": "",
            "isin": isin
        }])
    
    st.info(f"Dividends Distributed by ISIN: {isin}")
    st.dataframe(dividends_df)


def get_etf_element_data_clean(isin, element):
    # Call the FastAPI endpoint with a GET request
    response = requests.get(f"{FASTAPI_URL}/clean_element?isin={isin}&element={element}")

    if response.status_code == 200:
        record = response.json()
        if not record:
            return {}
        else:
            return record[element]

    else:
        st.error("Error fetching record from the server.")
        return {}


def merge_tables(tables, element):

    tables_df = [pd.DataFrame(list(tables[isin].items()), columns=[element, isin]) for isin in tables.keys()]
    return pd.concat(tables_df)


if st.button("Process ISIN"):
    for isin in selected_etfs:
        process_response = requests.post(
            f"{FASTAPI_URL}/process", json={"isin": isin}
        )
        st.text(f'Processing {isin}')
        st.text(process_response.text)

compare_button = True
# Button to fetch the maturity record
if compare_button and len(selected_etfs) > 0:
    
    tables_maturity = {}
    tables_rating = {}
    tables_market = {}
    tables_portfolio = {}
    
    for isin in selected_etfs:
        tables_maturity[isin] = get_etf_element_data_clean(isin, "maturity")
        tables_rating[isin] = get_etf_element_data_clean(isin, "credit_rate")
        tables_market[isin] = get_etf_element_data_clean(isin, "market_allocation")
        tables_portfolio[isin] = get_etf_element_data_clean(isin, "portfolio")

    df_merged = merge_tables(tables_portfolio, element='Portfolio')
    st.dataframe(df_merged)
    
    # Maturity
    df_merged = merge_tables(tables_maturity, element='Maturity')
    # Plot Comparison
    st.write("### Maturity Distribution Comparison")
    fig = px.bar(
        df_merged.melt(id_vars=["Maturity"], var_name="Table", value_name="Percentage"),
        x="Maturity",
        y="Percentage",
        color="Table",
        barmode="group",
        title="Comparison of Maturity Distributions",
    )
    st.plotly_chart(fig)

    ### RATING
    df_merged = merge_tables(tables_rating, element='Rating')
    # Plot Rating Breakdown
    st.write("### Rating Breakdown Comparison")
    fig_rating = px.bar(
        df_merged.melt(id_vars=["Rating"], var_name="Table", value_name="Percentage"),
        x="Rating",
        y="Percentage",
        color="Table",
        barmode="group",
        title="Comparison of Rating Breakdown",
    )

    fig_rating.update_layout(
        barmode="group",
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1,  # gap between bars of the same location coordinate.
    )
    st.plotly_chart(fig_rating)

    ### MARKET ALLOCATION
    # Standardizing Country Names (Removing extra words for consistency)

    df_merged = merge_tables(tables_market, element='Country')
    # Plot
    st.write("### Market Allocation Comparison")
    st.dataframe(df_merged)
    fig_market = px.bar(df_merged.melt(id_vars=['Country'], var_name='Table', value_name='Percentage'),
                        y='Country', x='Percentage', color='Table', barmode='group',
                        title="Comparison of Market Allocation",
                        orientation='h')  # Horizontal bars
    fig_market.update_layout(height=50*len(df_merged['Country']))
    st.plotly_chart(fig_market)

    