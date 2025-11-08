import os 
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import certifi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

if not TMDB_API_KEY or not MONGO_URI:
    raise ValueError("TMDB_API_KEY and MONGO_URI environment variables are required")

# MongoDB connection with SSL certificate and error handling
try:
    client = MongoClient(
        MONGO_URI, 
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where()  # Use certifi for SSL certificates
    )
    # Test connection
    client.admin.command('ping')
    db = client.get_database()  # Gets database from URI
    user_collection = db["users"]
    movie_collection = db["movies"]
    logger.info("MongoDB connection successful")
except ServerSelectionTimeoutError as e:
    logger.error(f"MongoDB connection failed: {e}")
    raise