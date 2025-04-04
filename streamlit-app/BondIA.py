import streamlit as st
import pandas as pd
import requests


# Set the page configuration
st.set_page_config(
    page_title="BondIA", 
    page_icon="📈",      
    layout="wide"        
)

FASTAPI_URL = "http://fastapi-app:8000"


json_records = requests.get(f"{FASTAPI_URL}/json-records").json()
pdf_records = requests.get(f"{FASTAPI_URL}/pdf-records").json()

# Call the FastAPI endpoint
get_avaliable_records = requests.get(f"{FASTAPI_URL}/records")

if get_avaliable_records.status_code == 200:
    records = get_avaliable_records.json()
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(records)

    # Create new columns for JSON and PDF with icons
    df['JSON'] = df['isin'].apply(lambda x: '✅' if x in json_records else '')
    df['PDF'] = df['isin'].apply(lambda x: '✅' if x in pdf_records else '')

    st.dataframe(df,  )
else:
    st.error("Error fetching records from the server.")


# Create a sidebar for the app
sidebar = st.sidebar
isin = sidebar.text_input("Isin")


if sidebar.button("Process Factsheet"):
    # Show a spinner while processing the request
    with st.spinner("Processing... Please wait."):
        process_response = requests.post(f"{FASTAPI_URL}/process", json={"isin": isin})
        print(process_response.text)
        st.text(process_response.text)