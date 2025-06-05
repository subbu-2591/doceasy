from pymongo import MongoClient
import os

# Get MongoDB URI from environment variable or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/doceasy')

# Create MongoDB client
client = MongoClient(MONGODB_URI)

# Get database instance
db = client.get_database() 