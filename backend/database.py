from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

# MongoDB Atlas connection string
uri = "mongodb+srv://subrahmanyag79:dhDShm338VxoPMUz@doceasy.kp4oh2g.mongodb.net/?retryWrites=true&w=majority&appName=doceasy"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Get database instance
db = client.get_database() 