import os
from typing import Optional, Dict, Any
from pymongo import MongoClient

# Load MongoDB credentials from environment variables
MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB connection string
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo:27017/"

class MongoDBUtils:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def create_collection(self, collection_name: str):
        """Create a new collection in the database."""
        return self.db.create_collection(collection_name)

    def insert_record(self, collection_name: str, record: Dict[str, Any]):
        """Insert a record into a specified collection."""
        collection = self.db[collection_name]
        result = collection.insert_one(record)
        return f"Record inserted with ID: {result.inserted_id}"

    def retrieve_record(self, collection_name: str, query: Dict[str, Any]):
        """Retrieve a record from a specified collection, excluding the _id field."""
        collection = self.db[collection_name]
        record = collection.find_one(query, {"_id": 0})
        return self.serialize_record(record)

    def record_exists(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Check if a record exists in a specified collection."""
        collection = self.db[collection_name]
        return collection.count_documents(query) > 0

    def close_connection(self):
        """Close the MongoDB client connection."""
        self.client.close()

    @staticmethod
    def serialize_record(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert MongoDB record to a serializable format."""
        if record and "_id" in record:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string
        return record

# Example usage:
# mongo_utils = MongoDBUtils(mongo_uri, "bonds")
# mongo_utils.create_collection("maturity")
# mongo_utils.insert_record("maturity", {"isin": "US1234567890", "maturity": "2025-12-31"})
# record = mongo_utils.retrieve_record("maturity", {"isin": "US1234567890"})
# exists = mongo_utils.record_exists("maturity", {"isin": "US1234567890"})
# mongo_utils.close_connection()
