import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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


table_sector_1 = {'Treasury': '100.05', 'Cash': '-0.05'}

table_sector_2 = {'Treasury': '99.9%', 'Cash': '0.1'}

table_rating_1 = {'Cash and/or Derivatives': '-0.05', 'AAA': '22.88', 'AA': '35.46', 'A': '18.49', 'BBB': '23.22'}

table_rating_2 = {'AAA': '22.8%', 'AA': '35.7', 'A': '17.8', 'BBB': '21.1', 'Not Rated': '2.5'}

table_market_1 = {'France': '23.7%', 'Italy': '22.2', 'Germany': '18.5', 'Spain': '14.3', 'Belgium': '5.2', 'Netherlands': '4.1%', 'Austria': '3.7', 'Portugal': '1.8', 'Finland': '1.6', 'Ireland': '1.5'}

table_market_2 = {'FRANCE (REPUBLIC OF)': '23.52%', 'ITALY (REPUBLIC OF)': '22.12%', 'GERMANY (FEDERAL REPUBLIC OF)': '18.57%', 'SPAIN (KINGDOM OF)': '14.35%', 'BELGIUM KINGDOM OF (GOVERNMENT)': '5.16%', 'NETHERLANDS (KINGDOM OF)': '4.10%', 'AUSTRIA (REPUBLIC OF)': '3.64%', 'PORTUGAL (REPUBLIC OF)': '1.95%', 'FINLAND (REPUBLIC OF)': '1.62%', 'IRELAND (GOVERNMENT)': '1.52%', 'Total of Portfolio': '96.55%'}


def clean_keys(table):
    table = {key.split(" ")[0].capitalize(): value for key, value in table.items() 
             if "Total" not in key and 'Derivatives' not in key}

    return table



def clean_tables(table_1, table_2, element):

    # Convert to DataFrame
    df1 = pd.DataFrame(list(table_1.items()), columns=[element, 'Value 1'])
    df2 = pd.DataFrame(list(table_2.items()), columns=[element, 'Value 2'])

    # Convert values to numeric
    df1['Value 1'] = df1['Value 1'].replace('%', '', regex=True).astype(float)
    df2['Value 2'] = df2['Value 2'].replace('%', '', regex=True).astype(float)

    df_merged = pd.merge(df1, df2, on=element, how='outer').fillna(0)
    return df1, df2, df_merged

# Streamlit App
# st.title("Maturity Tables Comparison")

# col1, col2 = st.columns(2)
# with col1:
#     st.write("### Table Maturity 1")
#     st.dataframe(df1)
# with col2:
#     st.write("### Table Maturity 2")
#     st.dataframe(df2)

# Maturity
df1, df2, df_merged = clean_tables(clean_keys(table_maturity_1), clean_keys(table_maturity_2), element='Maturity')
# Plot Comparison
st.write("### Maturity Distribution Comparison")
fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
             x='Maturity', y='Percentage', color='Table', barmode='group',
             title="Comparison of Maturity Distributions")
st.plotly_chart(fig)


# ### SECTOR
# df1, df2, df_merged = clean_tables(table_sector_1, table_sector_2, element='Sector')

# # Plot Sector Breakdown
# st.write("### Sector Breakdown Comparison")
# fig_sector = px.pie(df_merged.melt(id_vars=['Sector'], var_name='Table', value_name='Percentage'), 
#                     names='Sector', values='Percentage', color='Table',
#                     title="Comparison of Sector Breakdown")
# st.plotly_chart(fig_sector)


### RATING
df1, df2, df_merged = clean_tables(clean_keys(table_rating_1), clean_keys(table_rating_2), element='Rating')

# Plot Rating Breakdown
st.write("### Rating Breakdown Comparison")
fig_rating = px.bar(df_merged.melt(id_vars=['Rating'], var_name='Table', value_name='Percentage'), 
                    x='Rating', y='Percentage', color='Table', barmode='group',
                    title="Comparison of Rating Breakdown")

fig_rating.update_layout(barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)
st.plotly_chart(fig_rating)

### MARKET ALLOCATION
# Standardizing Country Names (Removing extra words for consistency)

df1, df2, df_market_merged = clean_tables(clean_keys(table_market_1), clean_keys(table_market_2), element='Country')
# Sort by first dataset for better comparison
df_market_merged = df_market_merged.sort_values(by="Value 1", ascending=False)

# Plot
st.write("### Market Allocation Comparison")
fig_market = px.bar(df_market_merged.melt(id_vars=['Country'], var_name='Table', value_name='Percentage'),
                    y='Country', x='Percentage', color='Table', barmode='group',
                    title="Comparison of Market Allocation",
                    orientation='h')  # Horizontal bars

st.plotly_chart(fig_market)