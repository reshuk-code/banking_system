import os
import pymongo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_db():
    try:
        # Connect to MongoDB using the URI from the environment variable
        my_client = pymongo.MongoClient(os.getenv("MONGO_URI_LOCAL"))
        my_db = my_client["banking"]

        # Check if the connection is successful by listing database names
        my_client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        return my_db
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    db = connect_db()
