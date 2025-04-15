import os
from typing import Optional, Dict, Any, Union, List
from pymongo import MongoClient, ASCENDING





class MongoDBUtils:
    def __init__(self, db_name: str = "bonds"):
        # Load MongoDB credentials from environment variables
        MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        # MongoDB connection string
        mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo:27017/"
        self.client = MongoClient(mongo_uri)
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
    
    def upsert_record(self, collection_name: str, record: Dict[str, Any], key_field: Union[str, List[str]]):
        """
        Upsert a record into a specified collection.
        If the record already exists based on the key_field, it will be replaced.
        Otherwise, a new record will be inserted.
        """

        # Ensure the key_field is a list for consistency
        key_fields = [key_field] if isinstance(key_field, str) else key_field

        collection = self.db[collection_name]

        # Create an index on the 'isin' field if it doesn't exist
        collection.create_index([(key_field[0], ASCENDING)], unique=True)

        collection = self.db[collection_name]

        filter_query = {field: record[field] for field in key_fields}

        # Use $set to update the fields in the record
        result = collection.update_one(
            filter_query,  # Filter by key_fields
            {"$set": record},  # Update the record
            upsert=True  # Insert if not found
        )
        
        return result

    

    def close_connection(self):
        """Close the MongoDB client connection."""
        self.client.close()


    @staticmethod
    def serialize_record(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert MongoDB record to a serializable format."""
        if record and "_id" in record:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string
        return record

# Example usage
if __name__ == "__main__":
    mongodb = MongoDBUtils()

    record = {
        "isin": "US0378331005",  # Example ISIN
        "name": "Apple Inc.",
        "price": 150.00
    }

    result = mongodb.upsert_record("test_1", record,"isin")
    print(result)