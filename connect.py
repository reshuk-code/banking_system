"""
This code belongs to reshuk-code.
Contact: business.reshuksapkota@gmail.com
GitHub: https://github.com/reshuk-code

This program is open source and built for a personal project.
You are free to use, modify, and distribute this code for non-commercial purposes.
However, commercial use of this code is strictly prohibited.

© 2025 Reshuk Sapkota. All rights reserved.
"""


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
