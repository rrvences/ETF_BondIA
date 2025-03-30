import streamlit as st
import pandas as pd
import plotly.express as px

# Data
table_maturity_1 = {
    'Under 1 Year': '0.1%', '1 - 5 Years': '41.1', '5 - 10 Years': '30.7',
    '10 - 15 Years': '10.0', '15 - 20 Years': '7.3', '20 - 25 Years': '3.6%',
    'Over 25 Years': '7.1'
}

table_maturity_2 = {
    'Cash and Derivatives': '-0.05', '0 - 1 Years': '1.36', '1 - 2 Years': '9.81',
    '2 - 3 Years': '10.88', '3 - 5 Years': '18.61', '5 - 7 Years': '13.12',
    '7 - 10 Years': '17.13', '10 - 15 Years': '10.23', '15 - 20 Years': '8.91',
    '20+ Years': '10.99'
}

# Convert to DataFrame
df1 = pd.DataFrame(list(table_maturity_1.items()), columns=['Maturity', 'Value 1'])
df2 = pd.DataFrame(list(table_maturity_2.items()), columns=['Maturity', 'Value 2'])

# Convert values to numeric
df1['Value 1'] = df1['Value 1'].replace('%', '', regex=True).astype(float)
df2['Value 2'] = df2['Value 2'].astype(float)

# Streamlit App
st.title("Maturity Tables Comparison")

col1, col2 = st.columns(2)
with col1:
    st.write("### Table Maturity 1")
    st.dataframe(df1)
with col2:
    st.write("### Table Maturity 2")
    st.dataframe(df2)

# Merging Data for Comparison
df_merged = pd.merge(df1, df2, on='Maturity', how='outer').fillna(0)

# Plot Comparison
st.write("### Maturity Distribution Comparison")
fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
             x='Maturity', y='Percentage', color='Table', barmode='group',
             title="Comparison of Maturity Distributions")
st.plotly_chart(fig)
