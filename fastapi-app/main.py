import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Callable, Any
from pipelines.extraction.extract_etfs_factsheet import extract_and_save_pdf
from pipelines.transform.parser_utils import parse_pdf_document
from pipelines.general.filesystem_utils import FS_PATH, JSON_PATH, CODE_PATH
from pipelines.mongo.mongo_utils import MongoDBUtils
from pipelines.transform.process_json_data import (extract_maturity,
                                                    extract_market_allocation, 
                                                    extract_credit_rate,
                                                    extract_sector
                                                    )



app = FastAPI()
mongodb = MongoDBUtils()


class IsinInput(BaseModel):
    isin: str


@app.get("/element")
def get_maturity(isin: str, element:str):
    # Fetch the maturity record using the helper function
    
    record = mongodb.retrieve_record(element,{"isin":isin})

    return record if record else {"error": "No record found"}


@app.post("/process")
def process_data(data: IsinInput):
    # Extract the ISIN from the input
    isin = data.isin

    # Define file paths
    pdf_path = f"{FS_PATH}{isin}_factsheet.pdf"
    json_save_path = f"{JSON_PATH}{isin}_factsheet.json"

    # Check if the PDF already exists
    if not os.path.exists(pdf_path):
        extract_and_save_pdf(isin)  # Only execute if PDF does not exist

    # Check if the JSON already exists
    if not os.path.exists(json_save_path):
        parse_pdf_document(isin)  # Only execute if JSON does not exist


    for element in ["maturity","sector","credit_rate","market_allocation"]:
        extract_element_and_insert_into_mongo(isin,element,json_save_path)
    
    return "Isin Processed"



def extract_element_and_insert_into_mongo(isin: str, element: str, json_save_path: str):
    """
    Extracts a specified element from a JSON file and inserts it into MongoDB if it doesn't already exist.

    Args:
        isin (str): The ISIN code for the record.
        element (str): The type of element to extract (e.g., "maturity", "sector", "credit_rate", "market_allocation").
        json_save_path (str): The path to the JSON file from which to extract the data.
    """
    # Mapping of element types to extraction functions
    function_dict: Dict[str, Callable[[str], Any]] = {
        "maturity": extract_maturity,
        "sector": extract_sector,
        "credit_rate": extract_credit_rate,
        "market_allocation": extract_market_allocation,
    }
    
    # Check if the provided element is valid
    if element not in function_dict:
        raise ValueError(f"Invalid element type: {element}. Must be one of {list(function_dict.keys())}.")

    # Check if the record already exists in MongoDB
    existing_record = mongodb.record_exists(element, {"isin": isin})

    if not existing_record:
        # If the record does not exist, extract the data
        extracted_data = function_dict[element](json_save_path)

        # Prepare the record for insertion
        record_data = {"isin": isin, element: extracted_data}

        # Insert the new record into MongoDB
        insert_result = mongodb.insert_record(element, record_data)
        print(insert_result)  # Optionally print the result of the insertion


@app.get("/records")
def get_records():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/etfs_ref_data.csv")
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)


@app.get("/pdf-records")
def get_pdf_records():
    # Read the CSV file into a DataFrame
    list_of_pdfs = os.listdir(FS_PATH)
    pdf_records = [ pdf.replace("_factsheet.pdf","") for pdf in list_of_pdfs]
    return pdf_records

@app.get("/json-records")
def get_json_records():
    # Read the CSV file into a DataFrame
    list_of_json = os.listdir(JSON_PATH)
    json_records = [ pdf.replace("_factsheet.json","") for pdf in list_of_json]
    return json_records
