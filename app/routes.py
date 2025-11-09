import logging
import bcrypt
import requests
from dotenv import load_dotenv
from .helper_functions import *
from flask import Blueprint, render_template, request, session, redirect, url_for,jsonify



load_dotenv()

# Create a Blueprint
main_routes = Blueprint('main', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


IMAGE_BASE = "https://image.tmdb.org/t/p/"


@main_routes.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503




@main_routes.route('/', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').encode('utf-8')

        if not username or not password:
            error = "Username and password are required"
            return render_template("login_page.html", error=error)

        try:
            user = user_collection.find_one({"username": username})
            if user and bcrypt.checkpw(password, user["password_hash"]):
                session["username"] = username
                session.permanent = True  
                return redirect(url_for("main.home_page"))
            else:
                error = "Invalid username or password"
        except Exception as e:
            logger.error(f"Login error: {e}")
            error = "An error occurred. Please try again."
        
        return render_template("login_page.html", error=error)
    
    return render_template("login_page.html")

@main_routes.route('/signup', methods=['POST','GET'])
def signup_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username', '').strip().lower()
        user_password = request.form.get('password', '')

        if not username or not user_password:
            error = "Username and password are required"
            return render_template("signup_page.html", error=error)

        if len(user_password) < 6:
            error = "Password must be at least 6 characters"
            return render_template("signup_page.html", error=error)

        try:
            if user_collection.find_one({"username": username}):
                error = "Username already exists"
                return render_template("signup_page.html", error=error)

            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            user_collection.insert_one({
                "username": username,
                "password_hash": hashed_password,
                "watched": [],
                "watch_list": [],
                "notifications": []
            })
            return redirect(url_for("main.login_page"))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            error = "An error occurred. Please try again."
            return render_template("signup_page.html", error=error)
    
    return render_template("signup_page.html")


@main_routes.route('/homepage', methods=['GET', 'POST'])
def home_page():
    username = session.get("username", "")
    if not username:
        return redirect(url_for("main.login_page"))
    
    username = username.lower()
    query_results = []

    try:
        # Fetch user's watched and watchlist
        user_doc = user_collection.find_one(
            {"username": username},
            {"_id": 0, "watched": 1, "watch_list": 1, "notifications": 1}
        )
        watched_count = len(user_doc.get('watched', [])) if user_doc else 0
        watchlist_count = len(user_doc.get('watch_list', [])) if user_doc else 0
        notifications_count = len(user_doc.get('notifications', [])) if user_doc else 0

        # If it's a POST request (user searched)
        if request.method == 'POST':
            user_query = request.form.get("query", "").strip().lower()
            if not user_query:
                # If empty search, just show default movies again
                query_results = list(movie_collection.aggregate([{"$sample": {"size": 10}}]))
                for movie in query_results:
                    movie.pop('_id', None)
                return render_template(
                    "homepage.html",
                    username=username.upper(),
                    movies=query_results,
                    watchlist_count=watchlist_count,
                    watched_count=watched_count,
                    notifications_count=notifications_count
                )

            # Check if movies for that query already exist in DB
            existing_movies = list(movie_collection.find({"user_query": user_query}))
            if existing_movies:
                for movie in existing_movies:
                    movie.pop('_id', None)
                query_results = existing_movies
            else:
                # Fetch new movies from API
                user_query_results = search_movie_by_api_key(user_query, TMDB_API_KEY)
                for movie in user_query_results:
                    query_results.append({
                        "user_query": user_query,
                        "id": movie.get("id"),
                        "title": movie.get("title"),
                        "release_date": movie.get("release_date"),
                        "overview": movie.get("overview"),
                        "vote_average": movie.get("vote_average"),
                        "vote_count": movie.get("vote_count"),
                        "poster_url": IMAGE_BASE + "w342" + movie.get("poster_path") if movie.get("poster_path") else None,
                        "reviews": [],
                    })
                if query_results:
                    movie_collection.insert_many(query_results)
        else:
            # If it's a GET request (user just logged in), show random movies
            query_results = list(movie_collection.aggregate([{"$sample": {"size": 20}}]))
            for movie in query_results:
                movie.pop('_id', None)

    except Exception as e:
        logger.error(f"Homepage error: {e}")
        watched_count = watchlist_count = notifications_count = 0

    return render_template(
        "homepage.html",
        username=username.upper(),
        movies=query_results,
        watchlist_count=watchlist_count,
        watched_count=watched_count,
        notifications_count=notifications_count
    )


@main_routes.route('/get_watchlist', methods=['GET'])
def get_watchlist():
    """API endpoint to get user's watchlist"""
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    username = username.lower()
    
    try:
        user_doc = user_collection.find_one(
            {"username": username},
            {"_id": 0, "watch_list": 1}
        )
        
        watchlist_ids = user_doc.get('watch_list', []) if user_doc else []
        
        # Fetch movie details for each movie in watchlist
        movies = []
        for movie_id in watchlist_ids:
            movie_details = get_movie_details_from_tmdb(movie_id)
            if movie_details:
                movies.append(movie_details)
        
        return jsonify({"movies": movies})
    except Exception as e:
        logger.error(f"Get watchlist error: {e}")
        return jsonify({"error": "Failed to fetch watchlist"}), 500
    
    

@main_routes.route('/get_notifications', methods=['GET'])
def get_notifications():
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    username = username.lower()
    
    try:
        user_doc = user_collection.find_one(
            {"username": username},
            {"_id": 0, "notifications": 1}
        )
        
        notifications = user_doc.get("notifications", []) if user_doc else []
        return jsonify({"notifications": notifications})
    except Exception as e:
        logger.error(f"Get notifications error: {e}")
        return jsonify({"error": "Failed to fetch notifications"}), 500
    

# Add this new route to app/routes.py

@main_routes.route('/mark_notification_seen', methods=['POST'])
def mark_notification_seen():
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        notification_index = data.get('notificationIndex')
        
        if notification_index is None:
            return jsonify({"error": "Notification index required"}), 400

        # Get user's notifications
        user_doc = user_collection.find_one(
            {"username": username.lower()},
            {"notifications": 1}
        )
        
        if not user_doc or 'notifications' not in user_doc:
            return jsonify({"error": "No notifications found"}), 404
        
        notifications = user_doc['notifications']
        
        # Check if index is valid
        if notification_index < 0 or notification_index >= len(notifications):
            return jsonify({"error": "Invalid notification index"}), 400
        
        # Remove the notification at the specified index
        notifications.pop(notification_index)
        
        # Update the user document with the new notifications array
        user_collection.update_one(
            {"username": username.lower()},
            {"$set": {"notifications": notifications}}
        )
        
        return jsonify({"message": "Notification marked as seen"})
    except Exception as e:
        logger.error(f"Mark notification seen error: {e}")
        return jsonify({"error": "Failed to mark notification as seen"}), 500
    

@main_routes.route('/get_watched', methods=['GET'])
def get_watched():
    """API endpoint to get user's watched movies"""
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    username = username.lower()
    
    try:
        user_doc = user_collection.find_one(
            {"username": username},
            {"_id": 0, "watched": 1}
        )
        
        watched_ids = user_doc.get('watched', []) if user_doc else []
        
        # Fetch movie details for each watched movie
        movies = []
        for movie_id in watched_ids:
            movie_details = get_movie_details_from_tmdb(movie_id)
            if movie_details:
                movies.append(movie_details)
        
        return jsonify({"movies": movies})
    except Exception as e:
        logger.error(f"Get watched error: {e}")
        return jsonify({"error": "Failed to fetch watched movies"}), 500
    

@main_routes.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """API endpoint to get detailed movie info"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        movie_data = response.json()
        db_movie = movie_collection.find_one({"id": movie_id}, {"_id": 0, "reviews": 1})
        reviews = db_movie.get("reviews", []) if db_movie else []

        movie_details = {
            "id": movie_data.get("id"),
            "title": movie_data.get("title"),
            "tagline": movie_data.get("tagline"),
            "overview": movie_data.get("overview"),
            "release_date": movie_data.get("release_date"),
            "runtime": movie_data.get("runtime"),
            "vote_average": round(movie_data.get("vote_average", 0), 1),
            "vote_count": movie_data.get("vote_count"),
            "genres": ", ".join([genre["name"] for genre in movie_data.get("genres", [])]),
            "poster_url": IMAGE_BASE + "w500" + movie_data.get("poster_path") if movie_data.get("poster_path") else None,
            "backdrop_url": IMAGE_BASE + "w1280" + movie_data.get("backdrop_path") if movie_data.get("backdrop_path") else None,
            "reviews": reviews
        }
        return jsonify(movie_details)
    except requests.RequestException as e:
        logger.error(f"Error fetching movie details: {e}")
        return jsonify({"error": "Movie not found"}), 404
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@main_routes.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        movie_id = data.get('movieId')
        
        if not movie_id:
            return jsonify({"error": "Movie ID required"}), 400

        result = user_collection.update_one(
            {"username": username.lower()},
            {"$addToSet": {"watch_list": movie_id}}
        )

        if result.modified_count > 0:
            message = "Movie added to your watchlist!"
        else:
            message = "Movie is already in your watchlist."
        return jsonify({"message": message})
    except Exception as e:
        logger.error(f"Add to watchlist error: {e}")
        return jsonify({"error": "Failed to add to watchlist"}), 500

@main_routes.route('/add_to_watched', methods=['POST'])
def add_to_watched():
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        movie_id = data.get('movieId')
        
        if not movie_id:
            return jsonify({"error": "Movie ID required"}), 400

        # Add to watched list
        result = user_collection.update_one(
            {"username": username.lower()},
            {"$addToSet": {"watched": movie_id}}
        )

        # Remove from watch list (if it exists there)
        user_collection.update_one(
            {"username": username.lower()},
            {"$pull": {"watch_list": movie_id}}
        )

        if result.modified_count > 0:
            message = "Movie marked as watched and removed from watch later!"
        else:
            message = "Movie is already in your watched list."
        return jsonify({"message": message})
    except Exception as e:
        logger.error(f"Add to watched error: {e}")
        return jsonify({"error": "Failed to add to watched"}), 500
    

@main_routes.route('/submit_reviews', methods=['POST'])
def submit_reviews():
    username = session.get("username", "")
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        movieId = data.get('movieId')
        reviewText = data.get('reviewText', '').strip()
        reviewdate = data.get('date')

        if not movieId or not reviewText:
            return jsonify({"error": "Movie ID and review text required"}), 400

        review = {
            "username": username,
            "reviewText": reviewText,
            "date": reviewdate
        }

        movie_collection.update_one(
            {"id": movieId},
            {"$push": {"reviews": review}},
            upsert=True
        )
        add_notification(movieId, reviewText, username)
        
        return jsonify({"message": "Review submitted successfully!"})
    except Exception as e:
        logger.error(f"Submit review error: {e}")
        return jsonify({"error": "Failed to submit review"}), 500
