from pymongo import MongoClient
from urllib.parse import quote_plus
import os

def get_mongodb_client():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    cluster = os.getenv("MONGO_CLUSTER")
    options = os.getenv("MONGO_OPTIONS")
    database_name = os.getenv("MONGO_DB")

    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)
    connection_string = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}/{options}"
    
    return MongoClient(connection_string), database_name