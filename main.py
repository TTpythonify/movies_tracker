from flask import Flask,render_template,request,redirect,url_for
from pymongo import MongoClient
import bcrypt


# Connect to local MongoDB server
client = MongoClient("mongodb://localhost:27017")

db = client["movie_tracker_db"] 
collection = db["users"]



app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        error = ''
        username = request.form.get('username').lower()
        password = request.form.get('password').encode('utf-8')

        user = collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password_hash"]):
            return render_template("homepage.html")
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

        if collection.find_one({"username": username}):
            error="Username already exists"
            return render_template("login_page.html",error=error)

        collection.insert_one({
            "username": username,
            "password_hash": hashed_password  
        })
        return redirect(url_for("login_page"))

    return render_template("signup_page.html")


if __name__ == "__main__":
    app.run(debug=True)