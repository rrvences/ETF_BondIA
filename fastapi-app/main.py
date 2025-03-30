import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from processing.extract_etfs_factsheet import extract_and_save_pdf
from processing.parser import parse_pdf_document

app = FastAPI()

# Load MongoDB credentials from environment variables
MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB connection string
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo:27017/"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["mydatabase"]
collection = db["mycollection"]

class IsinInput(BaseModel):
    isin: str

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