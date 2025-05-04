import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_utils import get_ref_data_as_df


# Set the page configuration
st.set_page_config(
    page_title="BondIA Country Financial Data", page_icon="", layout="wide"
)

interest_rates_df = get_ref_data_as_df("interest_rates")
credit_rates_df = get_ref_data_as_df("country_list_ratings")
credit_rates_guide_df = get_ref_data_as_df("credit_ratings_guide")
debt_to_gdp_df = get_ref_data_as_df("country_debt_to_gdp")


# List of European countries
european_countries = [
    'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 
    'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 
    'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 
    'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 
    'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 
    'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 
    'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania', 
      'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 
    'Spain', 'Sweden'
]

# Get the values associated with "Euro Area"
euro_area_row = interest_rates_df[interest_rates_df['Country'] == 'Euro Area'].iloc[0]



# Create a new DataFrame for European countries with the same other columns
europe_df = pd.DataFrame({

    col: [euro_area_row[col]] * len(european_countries) for col in interest_rates_df.columns  # Copy Euro Area GDP
})
europe_df.loc[:, 'Country'] = european_countries

# Concatenate the original DataFrame with the new European countries DataFrame
interest_rates_df = pd.concat([interest_rates_df, europe_df], ignore_index=True)

#interest_rates_df["Country"].replace('Euro Area', 'Europe', inplace=True)


# Streamlit app
st.title("Country Financial Data")

# Create tabs for navigation
tab1, tab2, tab3 = st.tabs(["Credit Rates", "Interest Rates", "Debt to GDP"])

# Credit Rates Tab
with tab1:
    st.header("Country Credit Rates")
    st.dataframe(credit_rates_df)

    st.header("Credit Rates Guide")
    st.dataframe(credit_rates_guide_df)


# Interest Rates Tab
with tab2:
    st.header("Country Interest Rates")
    fig = go.Figure(data=go.Choropleth(
        locations=interest_rates_df['Country'],
        z=interest_rates_df['Last'].astype(float),
        locationmode='country names',
        colorscale='blugrn',
        autocolorscale=False,
        text=interest_rates_df['Last'], # hover text
        marker_line_color='white',
        zmin = interest_rates_df['Last'].quantile(0.05),
        
        zmax = interest_rates_df['Last'].quantile(0.95),
        marker_line_width=0.5,# line markers between states
        colorbar=dict(
            title=dict(
                text="Interest Rates"
                )
        )
    ))
    fig.update_layout(
        title="Interest Rates by Country",
        geo=dict(
        showframe=False,
        showcoastlines=False,
        showcountries=True,
        countrycolor='#f5f5f5',
        projection_type='equirectangular'
    ))

    st.plotly_chart(fig)
    st.dataframe(interest_rates_df)

# Debt to GDP Tab
with tab3:
    st.header("Country Debt to GDP")

    # Create a word map for credit rates
    # fig = px.choropleth(
    #     debt_to_gdp_df,
    #     locations="Country",
    #     locationmode="country names",
    #     color="Last",
    #     hover_name="Country",
        
    #     marker_line_color='white',
    #     color_continuous_scale='Blues',
    #     #color_continuous_scale=px.colors.sequential.Plasma,
    #     title="Interest Rates by Country",
    # )
    
    fig = go.Figure(data=go.Choropleth(
        locations=debt_to_gdp_df['Country'],
        z=debt_to_gdp_df['Last'].astype(float),
        locationmode='country names',
        colorscale='Reds',
        autocolorscale=False,
        text=debt_to_gdp_df['Last'], # hover text
        marker_line_color='white',
        
        zmin = debt_to_gdp_df['Last'].quantile(0.05),
        
        zmax = debt_to_gdp_df['Last'].quantile(0.95),
        marker_line_width=0.5,# line markers between states
        colorbar=dict(
            title=dict(
                text="Debt to GDP"
                )
        )
    ))
    fig.update_layout(
        geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ))

    st.plotly_chart(fig)
    st.dataframe(debt_to_gdp_df)
