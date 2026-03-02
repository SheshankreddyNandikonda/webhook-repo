import os
from flask import Flask
from .extensions import mongo
from .routes import main
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)
    app.register_blueprint(main)
    return app