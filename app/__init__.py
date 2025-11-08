from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret")

    # MongoDB setup
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)
    app.db = client.get_default_database()

    # Register Blueprints
    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
