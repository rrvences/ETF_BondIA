from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://mongo:27017/")
db = client["mydatabase"]
collection = db["mycollection"]

class Record(BaseModel):
    name: str
    age: int

@app.post("/add")
async def add_record(record: Record):
    collection.insert_one(record.dict())
    return {"message": "Record added successfully!"}

@app.get("/records")
async def get_records():
    records = list(collection.find({}, {"_id": 0}))
    return records
