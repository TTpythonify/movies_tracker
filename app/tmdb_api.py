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

# MongoDB connection with SSL certificate - don't test connection at startup
try:
    client = MongoClient(
        MONGO_URI, 
        serverSelectionTimeoutMS=30000,  # Increased timeout
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        tlsCAFile=certifi.where(),
        retryWrites=True,
        w='majority'
    )
    db = client.get_database()
    user_collection = db["users"]
    movie_collection = db["movies"]
    logger.info("MongoDB client initialized (connection will be established on first use)")
except Exception as e:
    logger.error(f"MongoDB initialization failed: {e}")
    raise
