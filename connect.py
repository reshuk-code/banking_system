import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    try:
      
        my_client = pymongo.MongoClient(os.getenv("MONGO_URI_LOCAL"))
        my_db = my_client["banking"]

     
        my_client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        return my_db
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None


if __name__ == "__main__":
    db = connect_db()
