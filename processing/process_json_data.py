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
            return -1
        else:
            return tables[heading]

def process_table(data, heading):
    """Process one table from the json, the one that is after the heading
    """
    with open('processing/field_mappings.yaml', 'r') as file:
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
    # table is a list
    # pass first 
    if table == []:
        return {}
    cols = [col if col != '' else 'Column ' + str(i) for i, col in enumerate(table[0]) ]
    table = pd.DataFrame(table[1:], columns=cols)
    if table.shape[1] == 2:
        table_dict = dict(zip(table.iloc[:,0].values, table.iloc[:,1]))
    else:
        values = (table.iloc[:,1::2].T.values).reshape(-1)
        keys = (table.iloc[:,::2].T.values).reshape(-1)
        table_dict = dict(zip(keys, values))
    
    return table_dict

    
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

def extract_year_performance(json_file_path):
    field = "12-month Performance"
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)

def extract_market_allocation(json_file_path):
    field = "Market Allocation"
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)


def extract_credit_rate(json_file_path):
    field = "Credit Rating"
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)

def extract_sector(json_file_path):
    field = "Sector Breakdown"
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)

def extract_annualised_performance(json_file_path):
    field = "Annualised Performance"
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)


def extract_maturity(json_file_path:str):
    field = 'Maturity Breakdown'
    data = load_json(json_file_path)
    json_table = process_table(data, field)
    return convert_dict(json_table)


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
