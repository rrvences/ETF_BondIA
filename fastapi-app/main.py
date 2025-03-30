import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from processing.extract_etfs_factsheet import extract_and_save_pdf
from processing.parser import parse_pdf_document
from processing.process_json_data import extract_maturity
from bson import ObjectId
from typing import Any, Dict, Optional

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

@app.get("/maturity")
def get_maturity(isin: str):


    print(f"Here {isin}")

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


    return record if record else {"error": "No record found"}


@app.post("/extract")
def extract_data(data: IsinInput):
    
    # Dummy processing logic
    isin = data.isin
    extract_and_save_pdf(isin)
    return {"message": "Data Extracted and stored successfully!"}


@app.post("/parse")
def parse_data(data: IsinInput):
    
    # Dummy processing logic
    isin = data.isin
    parse_pdf_document(isin)
    return {"message": "Data Parsed and stored successfully!"}


@app.post("/process")
def process_data(data: IsinInput):
    
    # Dummy processing logic
    isin = data.isin

    jsons_save_path = f"/app/data/json/{isin}_factsheet.json"
    maturtity = extract_maturity(jsons_save_path)
    insert_record(isin,maturtity)
    return maturtity