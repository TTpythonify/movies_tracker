
import logging
import requests
from .tmdb_api import *
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_BASE = "https://image.tmdb.org/t/p/"


# --------------------- Helper Functions --------------------- #
def search_movie_by_api_key(query, api_key):
    """Search movies using TMDB API"""
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as e:
        logger.error(f"TMDB API error: {e}")
        return []

def get_movie_details_from_tmdb(movie_id):
    """Fetch movie details from TMDB API"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        movie_data = response.json()
        return {
            "id": movie_data.get("id"),
            "title": movie_data.get("title"),
            "release_date": movie_data.get("release_date"),
            "overview": movie_data.get("overview"),
            "vote_average": round(movie_data.get("vote_average", 0), 1),
            "vote_count": movie_data.get("vote_count"),
            "poster_url": IMAGE_BASE + "w342" + movie_data.get("poster_path") if movie_data.get("poster_path") else None,
        }
    except requests.RequestException as e:
        logger.error(f"Error fetching movie {movie_id}: {e}")
        return None
    

def add_notification(movie_id, review_text, reviewer):
    """Add notification to users who have movie in watchlist"""
    try:
        users_cursor = user_collection.find(
            {"watch_list": movie_id},
            {"_id": 0, "username": 1}
        )

        for user in users_cursor:
            username = user["username"].lower()
            # Don't notify the reviewer
            if username == reviewer.lower():
                continue
                
            notification = {
                "movie_id": movie_id,
                "reviewer": reviewer,
                "text": review_text,
                "date": datetime.utcnow().isoformat()
            }

            user_collection.update_one(
                {"username": username},
                {"$push": {"notifications": notification}}
            )
    except Exception as e:
        logger.error(f"Add notification error: {e}")

