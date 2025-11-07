import os
import bcrypt
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Environment variables
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_default_database() 
user_collection = db["users"]
movie_collection = db["movies"]

# TMDB image base URL
IMAGE_BASE = "https://image.tmdb.org/t/p/"

# --------------------- Helper Functions --------------------- #
def search_movie_by_api_key(query, api_key):
    """Search movies using TMDB API"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

def get_movie_details_from_tmdb(movie_id):
    """Fetch movie details from TMDB API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
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
    return None

# --------------------- Routes --------------------- #
@app.route('/', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username').lower()
        password = request.form.get('password').encode('utf-8')

        user = user_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password_hash"]):
            session["username"] = username
            return redirect(url_for("home_page"))
        else:
            error = "Invalid username or password"
            return render_template("login_page.html", error=error)
    return render_template("login_page.html")

@app.route('/signup', methods=['POST','GET'])
def signup_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username').lower()
        user_password = request.form.get('password')
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

        if user_collection.find_one({"username": username}):
            error = "Username already exists"
            return render_template("login_page.html", error=error)

        user_collection.insert_one({
            "username": username,
            "password_hash": hashed_password
        })
        return redirect(url_for("login_page"))
    return render_template("signup_page.html")

@app.route('/homepage', methods=['GET', 'POST'])
def home_page():
    username = session.get("username", "").lower()
    query_results = []

    # Fetch user's watched and watchlist safely
    user_doc = user_collection.find_one(
        {"username": username},
        {"_id": 0, "watched": 1, "watch_list": 1,"notifications": 1}
    )
    watched_count = len(user_doc.get('watched', [])) if user_doc else 0
    watchlist_count = len(user_doc.get('watch_list', [])) if user_doc else 0
    notifications_count = len(user_doc.get('notifications', [])) if user_doc else 0

    if request.method == 'POST':
        user_query = request.form.get("query", "").lower()
        existing_movies = list(movie_collection.find({"user_query": user_query}))

        if existing_movies:
            for movie in existing_movies:
                movie.pop('_id', None)
            query_results = existing_movies
        else:
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

    return render_template(
        "homepage.html",
        username=username.upper(),
        movies=query_results,
        watchlist_count=watchlist_count,
        watched_count=watched_count,
        notifications_count=notifications_count
    )

@app.route('/get_watchlist', methods=['GET'])
def get_watchlist():
    """API endpoint to get user's watchlist"""
    username = session.get("username", "").lower()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
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

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    username = session.get("username", "").lower()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
    user_doc = user_collection.find_one(
        {"username": username},
        {"_id": 0, "notifications": 1}
    )
    
    notifications = user_doc.get("notifications", []) if user_doc else []
    return jsonify({"notifications": notifications})


@app.route('/get_watched', methods=['GET'])
def get_watched():
    """API endpoint to get user's watched movies"""
    username = session.get("username", "").lower()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    
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



@app.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """API endpoint to get detailed movie info"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
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
        else:
            return jsonify({"error": "Movie not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.get_json()
    movie_id = data.get('movieId')
    username = data.get('username').lower()

    result = user_collection.update_one(
        {"username": username},
        {"$addToSet": {"watch_list": movie_id}}
    )

    if result.modified_count > 0:
        message = f"Movie added to your watchlist!"
    else:
        message = f"Movie is already in your watchlist."
    return jsonify({"message": message})

@app.route('/add_to_watched', methods=['POST'])
def add_to_watched():
    data = request.get_json()
    movie_id = data.get('movieId')
    username = data.get('username').lower()

    result = user_collection.update_one(
        {"username": username},
        {"$addToSet": {"watched": movie_id}}
    )

    if result.modified_count > 0:
        message = f"Movie marked as watched!"
    else:
        message = f"Movie is already in your watched list."
    return jsonify({"message": message})

@app.route('/submit_reviews', methods=['POST'])
def submit_reviews():
    data = request.get_json()
    movieId = data.get('movieId')
    reviewText = data.get('reviewText')
    username = data.get('username')
    reviewdate = data.get('date')

    review = {
        "username": username,
        "reviewText": reviewText,
        "date": reviewdate
    }


    movie_collection.update_one(
        {"id": movieId},
        {"$push": {"reviews": review}}
    )
    add_notification(movieId, reviewText, username)
    
    return jsonify({"message": "Review submitted successfully!"})



def add_notification(movie_id, review_text, reviewer):

    users_cursor = user_collection.find(
        {"watch_list": movie_id},
        {"_id": 0, "username": 1}
    )

    for user in users_cursor:
        username = user["username"].lower()
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



# --------------------- Run App --------------------- #
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000,threaded=False)

