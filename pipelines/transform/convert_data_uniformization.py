import pandas as pd
from pycountry import countries

def clean_and_convert_values(df):
    """
    Clean the values column by removing percentage signs and converting to float.
    If the total sum of values is below 10, assume the values are in percentage and multiply by 100.
    
    Args:
    df (pd.DataFrame): Input DataFrame with a 'Value' column.
    
    Returns:
    pd.DataFrame: Cleaned DataFrame with 'Value' column as float.
    """
    # Remove percentage signs and convert values to float
    df['Value'] = df['Value'].replace('%', '', regex=True).astype(float)
    
    # If the sum of values is small (less than 10), assume they're in percentage and convert
    if df['Value'].sum() < 10:
        df['Value'] = df['Value'] * 100  # Convert to percentage if needed
    return df

def map_to_maturity_ranges(df, element):
    """
    Map maturity periods in the DataFrame to predefined maturity ranges based on the given dictionary.
    
    Args:
    df (pd.DataFrame): Input DataFrame with 'Maturity' and 'Value' columns.
    labels_dict (dict): Dictionary mapping maturity ranges to index values.
    
    Returns:
    pd.DataFrame: DataFrame with maturity mapped to predefined ranges.
    """
    labels_dict = {
    '<1 year': [0], 
    '1-5 years': [1, 2, 3, 4], 
    '5-10 years': [5, 6, 7, 8, 9], 
    '10-15 years': [10, 11, 12, 13, 14], 
    '15-20 years': [15, 16, 17, 18, 19], 
    '>20 years': [20]
    }
    # Initialize a new dictionary for the aggregated values
    new_table = {key: 0 for key in labels_dict.keys()}
    
    for i in range(len(df)):
        key = df[element].iloc[i]
        
        # Check for ranges (e.g., "1 - 5 Years") and map them to the corresponding group
        if '-' in key:
            key_value = int(key.split('-')[0].strip())  # Extract the start of the range
            new_table_key = [key for key in labels_dict.keys() if key_value in labels_dict[key]]
        
        # Handle 'Under 1 Year' or '< 1 Year' as a special case
        elif key.lower().split(' ')[0].strip() in ['under', '<']:
            key_value = 0
            new_table_key = [key for key in labels_dict.keys() if key_value in labels_dict[key]]
        
        # Handle 'Over 25 Years' or '> 20 Years' as a special case
        elif key.lower().split(' ')[0].strip() in ['over', '>', '20+']:
            key_value = 20
            new_table_key = [key for key in labels_dict.keys() if key_value in labels_dict[key]]
        
        # If the key doesn't match any known ranges, raise a warning and set it to 0
        else:
            print(f'Key: {key} is not represented, please add')
            new_table_key = [key]  # Assign to the unique key
            new_table[key] = 0
        
        # Accumulate the value into the correct maturity range
        new_table[new_table_key[0]] += df['Value'].iloc[i]
    
    # Convert the dictionary back to a DataFrame for return
    return pd.DataFrame(list(new_table.items()), columns=[element, 'Value'])

def map_to_rating_ranges(df, element):
    """
    Map credit ratings in the DataFrame to predefined credit ranges based on the given dictionary.
    
    Args:
    df (pd.DataFrame): Input DataFrame with 'Maturity' and 'Value' columns.
    labels_dict (dict): Dictionary mapping maturity ranges to index values.
    
    Returns:
    pd.DataFrame: DataFrame with maturity mapped to predefined ranges.
    """
    # Initialize a new dictionary for the aggregated values

    new_table = {
    'AAA': 0, 
    'AA': 0, 
    'A': 0,
    'BBB': 0,
    'Not Rated': 0, 
    }
    
    for i in range(len(df)):
        key = df[element].iloc[i]
        if key in new_table.keys():
            new_table[key] = df['Value'].iloc[i]
        elif key.split(' ')[0].strip() in new_table.keys(): # more than one word
            new_table[key.split(' ')[0].strip()] = df['Value'].iloc[i]
        else:
            print(f'{key} not in {new_table.keys()}')
            new_table[key] = df['Value'].iloc[i]
    
    # Convert the dictionary back to a DataFrame for return
    return pd.DataFrame(list(new_table.items()), columns=[element, 'Value'])

def map_to_issuers_names(df, element):
    """
    Map issuers names in the DataFrame to predefined issuers names based on the given dictionary.
    
    Args:
    df (pd.DataFrame): Input DataFrame with 'Maturity' and 'Value' columns.
    labels_dict (dict): Dictionary mapping maturity ranges to index values.
    
    Returns:
    pd.DataFrame: DataFrame with maturity mapped to predefined ranges.
    """
    # Initialize a new dictionary for the aggregated values
    df['Issuers'] = df['Issuers'].str.capitalize()
    country_names = [country.name for country in countries]
    issuer_countries = [country for country in country_names if country in str(df['Issuers'])]
    new_countries = []
    for i, issuer in enumerate(df['Issuers']):
        country = [country for country in issuer_countries if country in issuer]
        if len(country) > 1:
            print(f"Issue: {len(country)} countries found for {issuer}")
        elif len(country) == 1:
            new_countries += country
        else:
            # print(f'Ignoring "{issuer}"...')
            # not a country, but should be included if there
            new_countries += [issuer]
    df['Issuers'] = new_countries
    return df

def uniformise_table(table, element):
    """
    Process a maturity table by cleaning the data and mapping it to predefined maturity ranges.
    
    Args:
    table (dict): A dictionary containing the maturity periods and their values.
    labels_dict (dict): A dictionary of predefined maturity ranges.
    
    Returns:
    pd.DataFrame: Processed DataFrame with the maturity periods grouped into predefined ranges.
    """
    # Step 1: Convert the table to a DataFrame
    df = pd.DataFrame(list(table.items()), columns=[element, 'Value'])
    
    # Step 2: Clean and convert the 'Value' column
    df = clean_and_convert_values(df)
    
    # Step 3: Map the maturity periods to predefined maturity ranges
    if element == 'Maturity':
        return map_to_maturity_ranges(df, element)
    elif element == 'Rating':
        return map_to_rating_ranges(df, element)
    elif element == 'Issuers':
        return map_to_issuers_names(df, element)
# Example usage with tables and labels

def merge_tables(table1, table2, element):
    """
    Merge two tables by processing them and combining the results.
    
    Args:
    table1 (dict): The first table (e.g., maturity or rating).
    table2 (dict): The second table (e.g., maturity or rating).
    element (str): The element type (e.g., 'Maturity' or 'Rating').
    
    Returns:
    pd.DataFrame: Merged DataFrame containing both tables' data.
    """
    # Process the tables with uniform formatting
    df1 = uniformise_table(table1, element)
    df2 = uniformise_table(table2, element)
    
    # Merge the processed tables
    return pd.merge(df1, df2, on=element, how='outer').fillna(0)


if __name__ == '__main__':

    # Example Tables (these could be different bond fact sheets)
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
    merge_tables(table_maturity_1, table_maturity_2, element='Maturity')
    
    table_rating_1 = {'Cash and/or Derivatives': '-0.05', 'AAA': '22.88', 'AA': '35.46', 'A': '18.49', 'BBB': '23.22'}

    table_rating_2 = {'AAA': '22.8%', 'AA': '35.7', 'A': '17.8', 'BBB': '21.1', 'Not Rated': '2.5'}
    
    merge_tables(table_rating_1, table_rating_2, element='Rating')

    
    table_market_1 = {'France': '23.7%', 'Italy': '22.2', 'Germany': '18.5', 'Spain': '14.3', 'Belgium': '5.2', 'Netherlands': '4.1%', 'Austria': '3.7', 'Portugal': '1.8', 'Finland': '1.6', 'Ireland': '1.5'}

    table_market_2 = {'FRANCE (REPUBLIC OF)': '23.52%', 'ITALY (REPUBLIC OF)': '22.12%', 'GERMANY (FEDERAL REPUBLIC OF)': '18.57%', 'SPAIN (KINGDOM OF)': '14.35%', 'BELGIUM KINGDOM OF (GOVERNMENT)': '5.16%', 'NETHERLANDS (KINGDOM OF)': '4.10%', 'AUSTRIA (REPUBLIC OF)': '3.64%', 'PORTUGAL (REPUBLIC OF)': '1.95%', 'FINLAND (REPUBLIC OF)': '1.62%', 'IRELAND (GOVERNMENT)': '1.52%', 'Total of Portfolio': '96.55%'}

    df = merge_tables(table_market_1, table_market_2, element='Issuers')
    print(df)
