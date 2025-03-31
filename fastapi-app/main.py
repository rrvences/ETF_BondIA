import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from processing.extract_etfs_factsheet import extract_and_save_pdf
from processing.process_utils.parser_utils import parse_pdf_document
from processing.process_utils.process_json_data import extract_maturity
from fastapi.responses import JSONResponse
from processing.process_utils.filesystem_utils import FS_PATH, JSON_PATH, CODE_PATH


app = FastAPI()

class IsinInput(BaseModel):
    isin: str


@app.get("/maturity")
def get_maturity(isin: str):
    # Fetch the maturity record using the helper function
    record = get_maturity_record(isin)

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

    # Check if maturity data already exists
    existing_record = get_maturity_record(isin)

    if existing_record:
        # If maturity data exists, return it
        maturity = existing_record
    else:
        # If maturity data does not exist, extract it
        maturity = extract_maturity(json_save_path)
        insert_record(isin, maturity)  # Insert the new maturity record

    return maturity

@app.get("/records")
def get_records():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}processing/ref_data/etfs_ref_data.csv")
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)


@app.get("/pdf-records")
def get_pdf_records():
    # Read the CSV file into a DataFrame
    list_of_pdfs = os.listdir(FS_PATH)
    pdf_records = [ pdf.replace("_factsheet.pdf") for pdf in list_of_pdfs]
    return pdf_records

@app.get("/json-records")
def get_json_records():
    # Read the CSV file into a DataFrame
    list_of_json = os.listdir(JSON_PATH)
    json_records = [ pdf.replace("_factsheet.json") for pdf in list_of_json]
    return json_records
