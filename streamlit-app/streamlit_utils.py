import streamlit as st
import requests
import pandas as pd
from typing import Optional, Union

FASTAPI_URL = "http://fastapi-app:8000"

def fetch_data(url: str) -> Optional[dict]:
    """Base function for API calls with error handling"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def handle_element_response(response_data: dict) -> Union[dict, pd.DataFrame]:
    """Handles common element response processing"""
    if "error" in response_data:
        st.error(response_data["error"])
        return pd.DataFrame()
    return response_data

def get_element_data(isin: str, element: str) -> Optional[dict]:
    """Get specific element data for an ISIN"""
    url = f"{FASTAPI_URL}/element?isin={isin}&element={element}"
    data = fetch_data(url)
    return data.get(element) if data else None


def get_collection_data(collection_name: str) -> Optional[dict]:
    """Get specific element data for an ISIN"""
    url = f"{FASTAPI_URL}/collection_data?collection_name={collection_name}"
    data = fetch_data(url)
    return data if data else None


def get_collection_data_as_df(collection_name: str) -> Optional[dict]:
    """Get specific element data for an ISIN"""
    data = get_collection_data(collection_name)
    return pd.DataFrame(data) if data else pd.DataFrame()

def get_etf_element_data_as_df(isin: str, element: str) -> pd.DataFrame:
    """Get element data as DataFrame"""
    data = get_element_data(isin, element)
    return pd.DataFrame(data) if data else pd.DataFrame()

def get_ref_data_as_df(endpoint: str) -> pd.DataFrame:
    """Get reference data from any endpoint as DataFrame"""
    url = f"{FASTAPI_URL}/{endpoint}"
    data = fetch_data(url)
    return pd.DataFrame(data) if data and "error" not in data else pd.DataFrame()


def list_of_isins_available() -> list:
    """Get a list of available ISINs"""
    url = f"{FASTAPI_URL}/json-records"
    data = fetch_data(url)
    return list(data.keys()) if data else []

def read_pdf_content(isin: str):
    pdf_response = requests.get(f"{FASTAPI_URL}/read_pdf?isin={isin}")
    if pdf_response.status_code == 200:
        pdf_content = pdf_response.content
    return pdf_content