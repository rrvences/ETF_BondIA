import streamlit as st
import requests

st.title("ETF BondIA")

fastapi_url = "http://fastapi-app:8000"


isin = st.text_input("Isin")

if st.button("Extract Factsheet"):
    response = requests.post(f"{fastapi_url}/extract", json={"isin": isin})


if st.button("Parse Factsheet"):
    response = requests.post(f"{fastapi_url}/parse", json={"isin": isin})