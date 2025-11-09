import os
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError, ConnectionFailure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

if not TMDB_API_KEY or not MONGO_URI:
    raise ValueError("TMDB_API_KEY and MONGO_URI environment variables are required")


try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        tls=True,                 
        retryWrites=True,
        w="majority"
    )

    db = client["movie_tracker_123"]


    # Define collections
    user_collection = db["users"]
    movie_collection = db["movies"]

    # Test the connection immediately
    client.admin.command("ping")
    logger.info("✅ Successfully connected to MongoDB Atlas (Production Mode)")

except (ServerSelectionTimeoutError, ConnectionFailure, ConfigurationError) as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    raise SystemExit("Database connection failed. Application stopped.")

except Exception as e:
    logger.error(f"❌ Unexpected MongoDB initialization error: {e}")
    raise SystemExit("Database initialization failed. Application stopped.")
