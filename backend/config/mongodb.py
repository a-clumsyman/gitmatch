from pymongo import MongoClient
from urllib.parse import quote_plus
import os
from fastapi import HTTPException

def get_mongodb_client():
    try:
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        cluster = os.getenv("MONGO_CLUSTER")
        options = os.getenv("MONGO_OPTIONS")
        database_name = os.getenv("MONGO_DB")

        if not all([username, password, cluster, options, database_name]):
            raise ValueError("Missing MongoDB environment variables")

        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        connection_string = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}/{options}"
        
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("MongoDB connection successful")
        return client, database_name
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )