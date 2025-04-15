import pandas as pd
from typing import Dict, Callable, Any
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
    df['Value'] = df['Value'].str.replace(',', '', regex=False)  # Remove thousands separator

    df['Units'] =df['Value'].str.extract(r'([^\d\.\s]+.*)$').fillna('')
    # Remove percentage signs and convert values to float
    df['Value'] = df['Value'].str.extract(r'(-?[\d.,]+)').astype(float)
    # if a Value is not a number it will be put in the units columns, so nan values will be filled by units
    df['Value'] = df['Value'].fillna(df['Units'])
    df.loc[df['Value']==df['Units'], 'Units'] = ''
 # Convert to percentage if needed
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
    # If the sum of values is small (less than 10), assume they're in percentage and convert
    if df['Value'].sum() < 10:
        df['Value'] = df['Value'] * 100 
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
    return new_table

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
    if df['Value'].sum() < 10:
        df['Value'] = df['Value'] * 100 
    
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
    return new_table

def map_to_issuers_names(df, element):
    """
    Map issuers names in the DataFrame to predefined issuers names based on the given dictionary.
    
    Args:
    df (pd.DataFrame): Input DataFrame with 'Maturity' and 'Value' columns.
    labels_dict (dict): Dictionary mapping maturity ranges to index values.
    
    Returns:
    pd.DataFrame: DataFrame with maturity mapped to predefined ranges.
    """
    if df['Value'].sum() < 10:
        df['Value'] = df['Value'] * 100 
    
    # Initialize a new dictionary for the aggregated values
    df[element] = df[element].str.capitalize()
    country_names = [country.name for country in countries]
    issuer_countries = [country for country in country_names if country in str(df[element])]
    labels_dict = {}
    for i, issuer in enumerate(df[element]):
        country = [country for country in issuer_countries if country in issuer]
        if len(country) > 1:
            print(f"Issue: {len(country)} countries found for {issuer}")
        elif len(country) == 1:
            labels_dict[country[0]] = df['Value'].iloc[i]
        else:
            # print(f'Ignoring "{issuer}"...')
            # not a country, but should be included if there
            labels_dict[issuer] = df['Value'].iloc[i]
    # df[element] = new_countries

    return labels_dict

def map_to_portfolio_keys(df, element):
    label_dict = {
        "Average Maturity (years)": 0,
        "Effective Duration (years)": 0,
        "Number of Bonds": 0,
        "Yield": 0
    }
    df[element] = df[element].str.capitalize()
    for i in range(len(df)):
        item = df[element].iloc[i]
        if 'maturity' in item.lower():
            # average maturity
            if 'y' in df['Units'].iloc[i]:
                label_dict['Average Maturity (years)'] = df['Value'].iloc[i]
        elif 'duration' in item.lower():
            if 'y' in df['Units'].iloc[i]:
                label_dict['Effective Duration (years)'] = df['Value'].iloc[i]
        elif 'number' in item.lower():
            label_dict['Number of Bonds'] = df['Value'].iloc[i]
        elif 'yield' in item.lower():
            label_dict['Yield'] = df['Value'].iloc[i]
        else:
            if df['Units'].iloc[i] != '':
                units = f" ({df['Units'].iloc[i]})"
            else:
                units = ""
            label_dict[df[element].iloc[i].split(':')[0].strip() + units] = df['Value'].iloc[i]

    return label_dict

def map_to_sector_ranges(df, element):

    return df

def map_to_year_performance(df, element):
    return df

def map_to_cum_performance(df, element):

    label_dict = {
        "Cumulative 1m": 0,
        "Cumulative 3m": 0,
        "Cumulative 6m": 0,
        "Cumulative YTD": 0,
        "Annualised 1y": 0,
        "Annualised 3y": 0,
        "Annualised 5y": 0,
        "Since Inception": 0
    }
    
    for i in range(len(df)):
        key = df[element].iloc[i]
        if 'benchmark' in key.lower():
                continue
        if 'cumulative' in key.lower():
            label_dict['Cumulative ' + key[-2:]] = df['Value'].iloc[i]
        elif 'annualised' in key.lower():
            label_dict['Annualised ' + key[-2:]] = df['Value'].iloc[i]
        else:
            label_dict[key] = df['Value'].iloc[i]
            #else:
                
    return label_dict


def clean_table(table, element):
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
    df = df.loc[df[element]!=''].copy() #
    # Step 2: Clean and convert the 'Value' column
    df = clean_and_convert_values(df)
    
    # Step 3: Map the maturity periods to predefined maturity ranges
    function_dict: Dict[str, Callable[[str], Any]] = {
        "maturity": map_to_maturity_ranges,
        "credit_rate": map_to_rating_ranges,
        "market_allocation": map_to_issuers_names,
        "sector": map_to_sector_ranges,
        'cumulative': map_to_cum_performance,
        'year': map_to_year_performance,
        'portfolio': map_to_portfolio_keys
    }
    
    table_dict = function_dict[element](df, element)

    return table_dict

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
    table_maturity_1 =  {'Cash and Derivatives': '0.25', '1 - 2 Years': '4.42', '2 - 3 Years': '7.56', '3 - 5 Years': '17.43', '5 - 7 Years': '21.01', '7 - 10 Years': '16.47', '10 - 15 Years': '10.25', '15 - 20 Years': '7.14', '20+ Years': '15.46'}
    table_rating_1 =  {'Cash and/or Derivatives': '0.25', 'AA Rated': '19.88', 'A Rated': '32.16', 'BBB Rated': '47.34', 'Not Rated': '0.38'}
    table_sector_1 =  {'Treasury': '99.75', 'Cash and/or Derivatives': '0.25', 'Government Related': '0.00'}      
    table_performance_1 =  {'Share Class - CUMULATIVE (%)\\<br/>1m': '-0.13', 'Share Class - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>3m': '-0.63', 'Share Class - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>6m': '-1.81', 'Share Class - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>YTD': '0.69', 'Share Class - ANNUALISED (% p.a.)\\<br/>1y': '4.53', 'Share Class - 3y': '-0.03', 'Share Class - 5y': '0.69', 'Share Class - Since Inception': '1.48', 'Benchmark - CUMULATIVE (%)\\<br/>1m': '-0.10', 'Benchmark - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>3m': '-0.60', 'Benchmark - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>6m': '-1.64', 'Benchmark - CUMULATIVE (%)\\<br/>ANNUALISED (% p.a.)\\<br/>YTD': '0.70', 'Benchmark - ANNUALISED (% p.a.)\\<br/>1y': '4.74', 'Benchmark - 3y': '0.18', 'Benchmark - 5y': '0.94', 'Benchmark - Since Inception': '1.98'}

    table_portfolio_1 =  {'Average Weighted Maturity :': '9.77 yrs', 'Effective Duration :': '7.26 yrs', 'Standard Deviation (3y) :': '10.73%', 'Yield To Maturity :': '4.08', '12m Trailing Yield :': '3.17%', '3y Beta :': '1.01', 'Number of Holdings :': '96'}
    table_maturity_2 =  {'Under 1 Year': '0.0%', '1 - 5 Years': '51.8%', '5 - 10 Years': '35.8%', '10 - 15 Years': '5.9%', '15 - 20 Years': '2.2%', '20 - 25 Years': '1.3%', 'Over 25 Years': '3.0%', '': ''}
    table_rating_2 =  {'AAA': '0.5%', 'AA': '6.9%', 'A': '41.9%', 'BBB': '50.8%', 'Not Rated': '0.0%'}
    table_sector_2 =  {'Corporate - industrials': '49.1%', 'Corporate - financial institutions': '42.8%', 'Corporate - utilities': '8.1%'}
    table_portfolio_2 =  {'Number of bonds': '3,533', 'Yield to worst': '3.05%', 'Average coupon': '2.7%', 'Average maturity': '5.0 years', 'Average quality': 'A-', 'Average duration': '4.5 years', 'Cash investment\\*': '-0.0%', 'Turnover rate': '18%'}
    table_performance_2 =  {'-------------------------- - 1 month': '-------', '-------------------------- - Quarter': '-------', '-------------------------- - Year to date': '------------', '-------------------------- - 1 year': '------', '-------------------------- - 3 years': '-------', '-------------------------- - 5 years': '-------', '-------------------------- - 10 years': '--------', '-------------------------- - Since inception': '---------------', 'Fund(Net of expenses) - 1 month': '0.58%', 'Fund(Net of expenses) - Quarter': '0.63%', 'Fund(Net of expenses) - Year to date': '1.07%', 'Fund(Net of expenses) - 1 year': '6.52%', 'Fund(Net of expenses) - 3 years': '0.78%', 'Fund(Net of expenses) - 5 years': '-0.15%', 'Fund(Net of expenses) - 10 years': '—', 'Fund(Net of expenses) - Since inception': '1.22%', 'Benchmark - 1 month': '0.60%', 'Benchmark - Quarter': '0.66%', 'Benchmark - Year to date': '1.04%', 'Benchmark - 1 year': '6.62%', 'Benchmark - 3 years': '0.92%', 'Benchmark - 5 years': '-0.02%', 'Benchmark - 10 years': '1.04%', 'Benchmark - Since inception': '1.31%'}

    df = merge_tables(table_maturity_1, table_maturity_2, element='Maturity')
    print(df)
    df = merge_tables(table_rating_1, table_rating_2, element='Rating')
    print(df)
    df = merge_tables(table_portfolio_1, table_portfolio_2, element='Portfolio')
    print(df)
    df = merge_tables(table_sector_1, table_sector_2, element='Sector')
    print(df)
    #df = merge_tables(table_year_1, table_year_2, element='Year')
    #print(df)
    df = merge_tables(table_performance_1, table_performance_2, element='Cumulative')
    print(df)

    # table_market_1 = {'France': '23.7%', 'Italy': '22.2', 'Germany': '18.5', 'Spain': '14.3', 'Belgium': '5.2', 'Netherlands': '4.1%', 'Austria': '3.7', 'Portugal': '1.8', 'Finland': '1.6', 'Ireland': '1.5'}

    # table_market_2 = {'FRANCE (REPUBLIC OF)': '23.52%', 'ITALY (REPUBLIC OF)': '22.12%', 'GERMANY (FEDERAL REPUBLIC OF)': '18.57%', 'SPAIN (KINGDOM OF)': '14.35%', 'BELGIUM KINGDOM OF (GOVERNMENT)': '5.16%', 'NETHERLANDS (KINGDOM OF)': '4.10%', 'AUSTRIA (REPUBLIC OF)': '3.64%', 'PORTUGAL (REPUBLIC OF)': '1.95%', 'FINLAND (REPUBLIC OF)': '1.62%', 'IRELAND (GOVERNMENT)': '1.52%', 'Total of Portfolio': '96.55%'}

    # df = merge_tables(table_market_1, table_market_2, element='Issuers')
    # print(df)
