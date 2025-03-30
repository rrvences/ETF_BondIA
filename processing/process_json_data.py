import json
import os
import pandas as pd

# Function to load JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Extract tables from 'items' field
def extract_tables(data):
    tables = {}
    last_heading = None
    for entry in data:
        for item in entry.get("items", []):
            if item.get("type") == "heading":
                last_heading = item['value']
            if item.get("type") == "table":
                tables[last_heading] = item["rows"]
    return tables

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



if __name__ == '__main__':

    json_dir = os.path.join(os.getcwd(), 'files', 'json')
    df_json = pd.DataFrame()
    
    for file in os.listdir(json_dir):

        json_file = os.path.join(json_dir, file)
        data = load_json(json_file)
        fields = extract_fields(data)
        df_fields = pd.DataFrame(fields, index=['type']).T
        df_fields.loc[:, 'file'] = file
        df_fields.reset_index(inplace=True)
        df_json = pd.concat((df_json, df_fields), ignore_index=True)
    print(fields)