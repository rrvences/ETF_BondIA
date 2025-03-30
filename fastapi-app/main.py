import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from processing.extract_etfs_factsheet import extract_and_save_pdf
from processing.parser import parse_pdf_document
from processing.process_json_data import extract_maturity
from bson import ObjectId
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

app = FastAPI()

class IsinInput(BaseModel):
    isin: str

# Load MongoDB credentials from environment variables
MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB connection string
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo:27017/"


def insert_record(isin, maturity_data):
    client = MongoClient(mongo_uri)
    
    # Create or connect to the database "bonds"
    db = client["bonds"]

    # Create or connect to the collection "maturity"
    collection = db["maturity"]

    # Create the record to insert
    record = {
        "isin": isin,
        "maturity": maturity_data
    }

    # Insert the record into the collection
    result = collection.insert_one(record)
    
    # Print the inserted ID (optional)
    return f"Record inserted with ID: {result.inserted_id}"


def serialize_record(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert MongoDB record to a serializable format."""
    if record:
        # Convert ObjectId to string
        record["_id"] = str(record["_id"])  # Convert ObjectId to string
    return record

def get_maturity_record(isin: str):
    """Fetch maturity record from MongoDB."""
    # Connect to the MongoDB client
    client = MongoClient(mongo_uri)

    # Create or connect to the database "bonds"
    db = client["bonds"]

    # Create or connect to the collection "maturity"
    collection = db["maturity"]

    # Query the collection for the record with the specified ISIN
    record = collection.find_one({"isin": isin}, {"_id": 0})

    # Close the client connection
    client.close()

    return record

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
    pdf_path = f"/app/data/factsheet/{isin}_factsheet.pdf"
    json_save_path = f"/app/data/json/{isin}_factsheet.json"

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
    df = pd.read_csv(f"/app/code/processing/etfs_ref_data.csv")
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)


@app.get("/pdf-records")
def get_pdf_records():
    # Read the CSV file into a DataFrame
    list_of_pdfs = os.listdir("/app/data/factsheet/")
    pdf_records = [ pdf.replace("_factsheet.pdf") for pdf in list_of_pdfs]
    return pdf_records

@app.get("/json-records")
def get_json_records():
    # Read the CSV file into a DataFrame
    list_of_json = os.listdir("/app/data/json/")
    json_records = [ pdf.replace("_factsheet.json") for pdf in list_of_json]
    return json_records
