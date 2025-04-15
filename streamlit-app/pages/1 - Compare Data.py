import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_pdf_viewer import pdf_viewer

# Set the page configuration
st.set_page_config(page_title="BondIA Comparator", page_icon="⚔️", layout="wide")

st.title("Compare ETF BondIA")

FASTAPI_URL = "http://fastapi-app:8000"

# Create a sidebar for the app
sidebar = st.sidebar


json_records = requests.get(f"{FASTAPI_URL}/json-records").json()
pdf_records = requests.get(f"{FASTAPI_URL}/pdf-records").json()


def fetch_available_records():
    # Call the FastAPI endpoint
    get_avaliable_records = requests.get(f"{FASTAPI_URL}/records")

    if get_avaliable_records.status_code == 200:
        records = get_avaliable_records.json()
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(records)

        # Create new columns for JSON and PDF with icons
        df["JSON"] = df["isin"].apply(lambda x: "✅" if x in json_records else "")
        df["PDF"] = df["isin"].apply(lambda x: "✅" if x in pdf_records else "")

        return df

    else:
        st.error("Error fetching records from the server.")
        return pd.DataFrame()


def read_pdf_content(isin: str):
    pdf_response = requests.get(f"{FASTAPI_URL}/read_pdf?isin={isin}")
    if pdf_response.status_code == 200:
        pdf_content = pdf_response.content
    return pdf_content


# Fetch and display records
df = fetch_available_records()

df.set_index("isin", inplace=True)
# Display the DataFrame
event_df = st.dataframe(
    df, use_container_width=True, on_select="rerun", selection_mode="single-row"
)


if event_df.get("selection", {}).get("rows"):
    selected_row = df.iloc[event_df.get("selection", {}).get("rows")].index[0]
else:
    selected_row = None

    # Check if a row is selected
if selected_row is not None:
    # Get the selected row's index
    selected_isin = selected_row  # Get the ISIN of the selected row

    options = ["Process Factsheet", "Get Prices and Details"]

    if selected_isin in pdf_records:
        options.extend(["View PDF"])

    # Choose an action
    action = st.selectbox("Choose an action", options)

    if st.button("Perform Action"):
        if action == "View PDF":
            try:
                pdf_viewer(
                    read_pdf_content(selected_isin)
                )  # Assuming this function displays the PDF
            except Exception:
                st.error("Failed to fetch PDF. Please try again.")

        if action == "Get Prices and Details":
            try:
                with st.spinner("Processing... Please wait."):
                    prices_response = requests.post(
                        f"{FASTAPI_URL}/extract_info?isin={selected_isin}"
                    )
                    dividens_response = requests.post(
                        f"{FASTAPI_URL}/extract_prices?isin={selected_isin}"
                    )
                    info_response = requests.post(
                        f"{FASTAPI_URL}/extract_dividends?isin={selected_isin}"
                    )
                    st.text(prices_response.text)
                    st.text(dividens_response.text)
                    st.text(info_response.text)
            except Exception:
                st.error("Failed to fetch PDF. Please try again.")

        elif action == "Process Factsheet":
            # Show a spinner while processing the request
            with st.spinner("Processing... Please wait."):
                process_response = requests.post(
                    f"{FASTAPI_URL}/process", json={"isin": selected_isin}
                )
                st.text(process_response.text)

        else:
            st.warning("Please select a valid action.")

    if selected_isin in pdf_records:
        st.download_button(
            label="Download PDF",
            data=read_pdf_content(selected_isin),
            file_name=f"{selected_isin}_factsheet.pdf",  # Use the selected ISIN for the file name
            mime="application/pdf",  # MIME type for PDF
        )
else:
    st.warning("Please select a row from the DataFrame.")


list_of_isins = requests.get(f"{FASTAPI_URL}/json-records").json()

isin1 = sidebar.selectbox("Isin1", list_of_isins)
isin2 = sidebar.selectbox("Isin2", list_of_isins)
compare_button = sidebar.button("Compare")


def get_element_data(isin, element):
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
    df1 = pd.DataFrame(list(table_1.items()), columns=[element, "Value 1"])
    df2 = pd.DataFrame(list(table_2.items()), columns=[element, "Value 2"])

    # Convert values to numeric
    df1["Value 1"] = df1["Value 1"].replace("%", "", regex=True).astype(float)
    df2["Value 2"] = df2["Value 2"].replace("%", "", regex=True).astype(float)

    df_merged = pd.merge(df1, df2, on=element, how="outer").fillna(0)
    return df1, df2, df_merged


def clean_keys(table):
    table = {
        key.split(" ")[0].capitalize(): value
        for key, value in table.items()
        if "Total" not in key and "Derivatives" not in key
    }

    return table


# Button to fetch the maturity record
if compare_button:
    table_maturity_1 = get_element_data(isin1, "maturity")
    table_maturity_2 = get_element_data(isin2, "maturity")

    table_rating_1 = get_element_data(isin1, "credit_rate")
    table_rating_2 = get_element_data(isin2, "credit_rate")

    table_market_1 = get_element_data(isin1, "market_allocation")
    table_market_2 = get_element_data(isin2, "market_allocation")

    # Maturity
    df1, df2, df_merged = clean_tables(
        clean_keys(table_maturity_1), clean_keys(table_maturity_2), element="Maturity"
    )
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
    df1, df2, df_merged = clean_tables(
        clean_keys(table_rating_1), clean_keys(table_rating_2), element="Rating"
    )

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

    df1, df2, df_market_merged = clean_tables(
        clean_keys(table_market_1), clean_keys(table_market_2), element="Country"
    )
    # Sort by first dataset for better comparison
    df_market_merged = df_market_merged.sort_values(by="Value 1", ascending=False)

    # Plot
    st.write("### Market Allocation Comparison")
    fig_market = px.bar(
        df_market_merged.melt(
            id_vars=["Country"], var_name="Table", value_name="Percentage"
        ),
        y="Country",
        x="Percentage",
        color="Table",
        barmode="group",
        title="Comparison of Market Allocation",
        orientation="h",
    )  # Horizontal bars

    st.plotly_chart(fig_market)
