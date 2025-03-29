import os
import streamlit as st
import json
import pandas as pd



# Load JSON file
# json directory
FILES_DIR = "C:\\Users\\Mariana (pessoal)\\dev\\ETF_BondIA\\files\\json"
# select file
json_file = os.path.join(FILES_DIR, os.listdir(FILES_DIR)[0])

data = extract_data.load_json(json_file)

# Extract tables
tables = extract_data.extract_tables(data)

# Streamlit UI
st.title("📊 Extracted Tables from PDF")

if tables:
    for i, table_title in enumerate(tables):
        table = tables[table_title]
        col_names = [col if col != '' else str(i) for i, col in enumerate(table[0])]
        df = pd.DataFrame(table[1:], columns=col_names)  # Convert to DataFrame
        st.subheader(f"{table_title}")
        st.dataframe(df)
else:
    st.warning("No tables found in the document.")

