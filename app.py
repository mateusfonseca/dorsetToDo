"""
This file defines the general settings for the project.
"""

import os

from bson import ObjectId
from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient

from models import User

# connect to instance of MongoDB Atlas database
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.flask_db


def create_app():  # creates an app instance to be run
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # configures app's secret key
    app.config['DATABASE'] = db  # configures app's database

    # registers blueprint for app's auth routes
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # registers blueprint for app's main routes
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # instantiates LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # LoginManager fetches user instance from MongoDB
    # and returns it logged-in if it exists
    @login_manager.user_loader
    def load_user(user_id):
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            return User(user)

    # returns app instance
    return app
