import bcrypt
from test import solutions
from tmdb import *
from keys import my_secret_key
from pymongo import MongoClient
from flask import Flask,render_template,request,redirect,url_for,session,jsonify


# Connect to local MongoDB server
client = MongoClient("mongodb://localhost:27017")

db = client["movie_tracker_db"] 
user_collection = db["users"]
movie_collection = db["movies"]
IMAGE_BASE = "https://image.tmdb.org/t/p/"



app = Flask(__name__)
app.secret_key = my_secret_key

@app.route('/', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username').lower()
        password = request.form.get('password').encode('utf-8')

        user = user_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password_hash"]):
            # Store username in the session 
            session["username"] = username
            return redirect(url_for("home_page"))
        else:
            error = "Invalid username or password"

            return render_template("login_page.html",error=error)
    return render_template("login_page.html")



@app.route('/signup', methods = ['POST','GET'])
def signup_page():
    if request.method == 'POST':
        error=''
        username = request.form.get('username').lower()
        user_password = request.form.get('password')
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

        if user_collection.find_one({"username": username}):
            error="Username already exists"
            return render_template("login_page.html",error=error)

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

    # Fetch user watched list safely
    user_doc = user_collection.find_one({"username": username}, {"_id": 0, "watched": 1})
    watched_count = len(user_doc.get('watched', []))  # default to empty list if field missing

    if request.method == 'POST':
        user_query = request.form.get("query", "").lower()

        # Check if this query was already stored
        existing_movies = list(movie_collection.find({"user_query": user_query}))

        if existing_movies:
            print("I am displaying it from the database")
            for movie in existing_movies:
                movie.pop('_id', None)
            query_results = existing_movies

        else:
            user_query_results = search_movie_by_api_key(user_query, api_key)
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
                })

            if query_results:
                movie_collection.insert_many(query_results)
                print(f"\nI have added it {user_query}\n\n")

    return render_template(
        "homepage.html",
        username=username.upper(),
        movies=query_results,
        watchlist_count=watched_count,
        watched_count=0
    )



@app.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """API endpoint to get detailed movie information"""
    try:
        # Fetch detailed movie info from TMDB API
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        
        if response.status_code == 200:
            movie_data = response.json()
            
            # Format the response
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
                "backdrop_url": IMAGE_BASE + "w1280" + movie_data.get("backdrop_path") if movie_data.get("backdrop_path") else None
            }
            
            return jsonify(movie_details)
        else:
            return jsonify({"error": "Movie not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watched():
    data = request.get_json()
    movie_id = data.get('movieId')
    username = data.get('username').lower()
    
    result = user_collection.update_one(
        {"username": username},           
        {"$addToSet": {"watched": movie_id}}  # Adds only if not present
    )

    print(" i am here now ", result)
    
    if result.modified_count > 0:
        message = f"Movie {movie_id} marked as watched for {username}."
        print(message)
    else:
        message = f"Movie {movie_id} is already in {username}'s watched list."
        print(message)

    return jsonify({"message": message})




def get_movies_info(movie_id):
    movie = movie_collection.find_one({"id":movie_id},{"_id": 0})
    return movie 




if __name__ == "__main__":
    app.run(debug=True)