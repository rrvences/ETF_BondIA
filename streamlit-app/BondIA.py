import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import pandas as pd
import requests

# Set the page configuration
st.set_page_config(
    page_title="BondIA", 
    page_icon="📈",      
    layout="wide"        
)

# Create a sidebar for the app
sidebar = st.sidebar

FASTAPI_URL = "http://fastapi-app:8000"


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
        df['JSON'] = df['isin'].apply(lambda x: '✅' if x in json_records else '')
        df['PDF'] = df['isin'].apply(lambda x: '✅' if x in pdf_records else '')
    
        return df

    else:
        
        st.error("Error fetching records from the server.")
        return pd.DataFrame()



def read_pdf_content(isin:str):
    pdf_response = requests.get(f"{FASTAPI_URL}/read_pdf?isin={isin}")
    if pdf_response.status_code == 200:
        pdf_content = pdf_response.content
    return pdf_content

def main():

    # Fetch and display records
    df = fetch_available_records()

    df.set_index('isin',inplace=True)
    # Display the DataFrame
    event_df = st.dataframe(df, use_container_width=True,on_select='rerun', selection_mode = 'single-row')


    if event_df.get("selection",{}).get("rows"):
        selected_row = df.iloc[event_df.get("selection",{}).get("rows")].index[0] 
    else:
        selected_row = None

     # Check if a row is selected
    if selected_row is not None:

        # Get the selected row's index
        selected_isin = selected_row  # Get the ISIN of the selected row

        options = ["Process Factsheet","Get Prices and Details"]

        if selected_isin in pdf_records:
            options.extend(["View PDF"])

        # Choose an action
        action = st.selectbox("Choose an action", options)

        if st.button("Perform Action"):
            if action == "View PDF":
                try:
                    pdf_viewer(read_pdf_content(selected_isin))  # Assuming this function displays the PDF
                except Exception:
                    st.error("Failed to fetch PDF. Please try again.")
            
            if action == "Get Prices and Details":
                try:
                   with st.spinner("Processing... Please wait."):
                    prices_response = requests.post(f"{FASTAPI_URL}/extract_info?isin={selected_isin}")
                    dividens_response = requests.post(f"{FASTAPI_URL}/extract_prices?isin={selected_isin}")
                    info_response = requests.post(f"{FASTAPI_URL}/extract_dividends?isin={selected_isin}")
                    st.text(prices_response.text)
                    st.text(dividens_response.text)
                    st.text(info_response.text)
                except Exception:
                    st.error("Failed to fetch PDF. Please try again.")

            elif action == "Process Factsheet":
                # Show a spinner while processing the request
                with st.spinner("Processing... Please wait."):
                    process_response = requests.post(f"{FASTAPI_URL}/process", json={"isin": selected_isin})
                    st.text(process_response.text)

            else:
                st.warning("Please select a valid action.")

        if selected_isin in pdf_records:
            st.download_button(
                label="Download PDF",
                data=read_pdf_content(selected_isin),
                file_name=f"{selected_isin}_factsheet.pdf",  # Use the selected ISIN for the file name
                mime="application/pdf"  # MIME type for PDF
            )
    else:
        st.warning("Please select a row from the DataFrame.")


if __name__ == "__main__":
    main()