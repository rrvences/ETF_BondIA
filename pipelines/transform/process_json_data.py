import json
import os
import yaml
import pandas as pd
from functools import partial
from pipelines.general.filesystem_utils import CODE_PATH


# Function to load JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Extract tables from 'items' field
def extract_tables(data, mode='all', heading=''):
    tables = {}
    last_heading = None
    for entry in data:
        for item in entry.get("items", []):
            if item.get("type") == "heading":
                last_heading = item['value']
            if item.get("type") == "table":
                tables[last_heading] = item["rows"]
    if mode == 'all':
        return tables
    else:
        if heading not in tables.keys():
            return -1
        else:
            return tables[heading]



def process_table(data, heading):
    """Process one table from the json, the one that is after the heading
    """
    with open(f'{CODE_PATH}pipelines/ref_data/field_mappings.yaml', 'r') as file:
        field_mappings = yaml.safe_load(file)['field_mappings']
    map_list = field_mappings[heading]
    for map in map_list:
        table = extract_tables(data, mode='single', heading=map)
        if table != -1:
            break
    if table == -1:
        return []
    else: 
        return table



def convert_dict(table):
    # Check if the input table is empty
    if table == []:
        return {}  # Return an empty dictionary if the table is empty

    # Create a list of column names, replacing empty strings with 'Column X'
    # where X is the index of the column
    cols = [col if col != '' else 'Column ' + str(i) for i, col in enumerate(table[0])]

    # Convert the table (list of lists) into a pandas DataFrame, using the first row as column names
    table = pd.DataFrame(table[1:], columns=cols)

    # Check if the DataFrame has exactly 2 columns
    if table.shape[1] == 2:
        # If there are 2 columns, create a dictionary by zipping the first column (keys) with the second column (values)
        table_dict = dict(zip(table.iloc[:, 0].values, table.iloc[:, 1]))
    else:
        # If there are more than 2 columns, assume the keys are in the odd-indexed columns and values in the even-indexed columns
        # Reshape the values and keys into a flat array
        values = (table.iloc[:, 1::2].T.values).reshape(-1)  # Get values from even-indexed columns
        keys = (table.iloc[:, ::2].T.values).reshape(-1)     # Get keys from odd-indexed columns
        
        # Create a dictionary by zipping the keys and values
        table_dict = dict(zip(keys, values))
    
    return table_dict  # Return the constructed dictionary


    
def extract_fields(data):
    fields = {}
    last_heading = None
    for entry in data:
        for item in entry.get('items', []):
            if item.get("type") == "heading":
                last_heading = item['value']
            else:
                fields[last_heading] = item['type']
    return fields


def extract_data(json_file_path: str, field: str):
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)

# Create partial functions for each specific extraction
extract_year_performance = partial(extract_data, field="12-month Performance")
extract_market_allocation = partial(extract_data, field="Market Allocation")
extract_credit_rate = partial(extract_data, field="Credit Rating")
extract_sector = partial(extract_data, field="Sector Breakdown")
extract_annualised_performance = partial(extract_data, field="Annualised Performance")
extract_maturity = partial(extract_data, field="Maturity Breakdown")


if __name__ == '__main__':

    json_dir = os.path.join(os.getcwd(), 'files', 'json')
    for file in os.listdir(json_dir):
        
        json_file = os.path.join(json_dir, file)
        data = load_json(json_file)
        json_table = extract_maturity(json_file)
        print(json_table)

        json_table = extract_credit_rate(json_file)
        print(json_table)
        
        json_table = extract_sector(json_file)
        print(json_table)
