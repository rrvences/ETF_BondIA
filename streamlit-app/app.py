import streamlit as st
import pandas as pd
import requests


st.title("ETF BondIA")

fastapi_url = "http://fastapi-app:8000"


isin = st.text_input("Isin")

if st.button("Extract Factsheet"):
    response = requests.post(f"{fastapi_url}/extract", json={"isin": isin})


if st.button("Parse Factsheet"):
    response = requests.post(f"{fastapi_url}/parse", json={"isin": isin})


if st.button("Process Factsheet"):
    process_response = requests.post(f"{fastapi_url}/process", json={"isin": isin})
    print(process_response.text)
    st.text(process_response.text)


# Button to fetch the maturity record
if st.button("Get Maturity Record"):
    if isin:
        # Call the FastAPI endpoint with a GET request
        response = requests.get(f"{fastapi_url}/maturity?isin={isin}")

        if response.status_code == 200:
                record = response.json()
                if "error" not in record:
                    # Convert the record to a DataFrame for display
                    df = pd.DataFrame([record])
                    st.write("Maturity Record:")
                    st.dataframe(df)
                else:
                    st.error(record["error"])
        else:
            st.error("Error fetching record from the server.")
    else:
        st.warning("Please enter a valid ISIN.")