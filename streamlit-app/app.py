import streamlit as st
import requests

st.title("MongoDB Streamlit App")

# Input fields for data
name = st.text_input("Name")
age = st.number_input("Age", min_value=0)

if st.button("Add Record"):
    if name and age:
        response = requests.post("http://fastapi-app:8000/add", json={"name": name, "age": age})
        if response.status_code == 200:
            st.success("Record added successfully!")
        else:
            st.error("Failed to add record.")
    else:
        st.error("Please fill in all fields.")

# AI Processing Section
st.header("AI Processing")

value = st.number_input("Value for AI Processing", min_value=0.0)

if st.button("Process Data"):
    if value:
        response = requests.post("http://processing-app:8001/process", json={"value": value})
        if response.status_code == 200:
            st.success("Data processed successfully!")
            st.json(response.json())
        else:
            st.error("Failed to process data.")
    else:
        st.error("Please enter a value.")