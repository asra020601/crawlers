import os
import json
import argparse
from pymongo import MongoClient

def save_json_file_to_mongodb(file_path, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Loads a JSON file from the provided file path and inserts its data into a MongoDB collection.
    
    Parameters:
    - file_path: Path to the JSON file.
    - db_name: Name of the MongoDB database.
    - collection_name: Name of the collection where documents will be inserted.
    - mongo_uri: MongoDB URI string.
    """
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Open and load the JSON file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            # If the JSON contains a list of documents, insert them all at once.
            if isinstance(data, list):
                result = collection.insert_many(data)
                print(f"Inserted {len(result.inserted_ids)} documents from {file_path}")
            else:
                result = collection.insert_one(data)
                print(f"Inserted document with id {result.inserted_id} from {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save a JSON file to MongoDB.")
    parser.add_argument("filepath", help="Direct path to the JSON file")
    parser.add_argument("--db", default="your_database", help="Name of the MongoDB database")
    parser.add_argument("--collection", default="your_collection", help="Name of the MongoDB collection")
    parser.add_argument("--uri", default="mongodb://localhost:27017/", help="MongoDB connection URI")

    args = parser.parse_args()
    # Ensure that the provided path exists
    if not os.path.isfile(args.filepath):
        print(f"The file {args.filepath} does not exist. Please provide a valid file path.")
    else:
        save_json_file_to_mongodb(args.filepath, args.db, args.collection, args.uri)
