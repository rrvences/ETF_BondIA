import json
import os
import yaml
import pandas as pd

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
            print(f'Table for {heading} not found')
            return -1
        else:
            return tables[heading]

def process_table(data, heading):
    """Process one table from the json, the one that is after the heading
    """
    with open('/app/code/processing/field_mappings.yaml', 'r') as file:
        field_mappings = yaml.safe_load(file)['field_mappings']
    map_list = field_mappings[heading]
    for map in map_list:
        table = extract_tables(data, mode='single', heading=map)
        if table != -1:
            break
    if table == -1:
        return {}
    cols = [col if col != '' else 'Column ' + str(i) for i, col in enumerate(table[0]) ]
    table = pd.DataFrame(table[1:], columns=cols)
    return table.to_dict()

    
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


def convert_dict(input_dict):

    print(input_dict)

    # Extract the values from the input dictionary
    keys = input_dict["Column 0"]
    values = input_dict["Column 1"]
    
    # Create a new dictionary to hold the result
    result = {}
    
    # Iterate through the keys and values to populate the result dictionary
    for i in range(len(keys)):
        result[keys[i]] = values[i]
    
    return result


def extract_maturity(json_file_path:str):
    field = 'Maturity breakdown'
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)

if __name__ == '__main__':
    print("Here")