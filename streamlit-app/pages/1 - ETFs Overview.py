import streamlit as st
import pandas as pd
import requests
from streamlit_pdf_viewer import pdf_viewer
from streamlit_utils import get_ref_data_as_df, read_pdf_content, get_collection_data_as_df, FASTAPI_URL, list_of_pdfs_available

# Set the page configuration
st.set_page_config(page_title="BondIA Comparator", page_icon="⚔️", layout="wide")

st.title("Bond ETFs Overview")

# Text input for name filter
name_filter = st.text_input("Enter name to filter:")

# Fetch and display records
df_etfs_list = get_ref_data_as_df("etfs_list")
df_etf_info_status = get_collection_data_as_df("etf_info_status")


def status_check(group):
    return "Succeeded" if (group['status'] == "Succeeded").all() else "Error Processing"

df_etf_info_status_grouped = (
    df_etf_info_status
    .groupby('isin')
    .apply(status_check)
    .reset_index(name='status_result')
)


df = (
    df_etfs_list
    .merge(df_etf_info_status_grouped, on='isin', how='left')
    .fillna({'status_result': "No Process attempt"})
)

# Filter DataFrame based on input (case-insensitive)
if name_filter:
    df = df[df['name'].str.contains(name_filter, case=False, na=False)]


df.set_index("isin", inplace=True)
df.sort_values(by="status_result",inplace=True)
pdf_records = list_of_pdfs_available()

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

    df_etf_info_status.query(f" isin == '{selected_isin}' ")


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
                    f"{FASTAPI_URL}/process_fs_data", json={"isin": selected_isin}
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
    st.warning("Please select a row from the DataFrame to perform actions")