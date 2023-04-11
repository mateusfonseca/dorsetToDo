"""
This file defines the views for the app's auth routes.
They are functions that respond to web requests with the appropriate web responses.
They invoke the templates that will be rendered in return (if applicable) and handle any errors
that may arise during the handling of the requests, as well as redirections.
"""

from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import User

# creates blueprint for app's auth routes
auth = Blueprint('auth', __name__)


# login method allows existing users to log in to the app
@auth.route('/login', methods=('GET', 'POST'))  # accepts GET and POST requests at specified URL
def login():  # no parameters needed
    if current_user.is_authenticated:  # if user is logged-in
        return redirect(url_for('main.index'))  # redirects to home page
    else:  # if user is not logged-in
        if request.method == 'POST':  # if request method is POST
            email = request.form.get('email')  # field 'email' from submitted form
            password = request.form.get('password')  # field 'password' from submitted form
            remember = True if request.form.get('remember') else False  # field 'remember' from submitted form

            # fetches user from database by email
            user = db.users.find_one({'email': email})

            # if user with provided email was not found or passwords did not match
            if not user or not check_password_hash(user['password'], password):
                # renders error message to be displayed
                flash('Please check your login details and try again.')
                # redirects to login page
                return redirect(url_for('auth.login'))

            # if user was found and password checked
            model = User(user)  # create local instance of User with JSON-like document from database

            # logs user in with LoginManager
            login_user(model, remember=remember)
            return redirect(url_for('main.index'))  # redirects to home page
        else:  # if request method is GET
            return render_template('login.html')  # renders login template


# signup method allows new users to create an account
@auth.route('/signup', methods=('GET', 'POST'))  # accepts GET and POST requests at specified URL
def signup():  # no parameters needed
    if current_user.is_authenticated:  # if user is logged-in
        return redirect(url_for('main.index'))  # redirects to home page
    else:  # if user is not logged-in
        if request.method == 'POST':  # if request method is POST
            email = request.form.get('email')  # field 'email' from submitted form
            name = request.form.get('name')  # field 'name' from submitted form
            password = request.form.get('password')  # field 'password' from submitted form

            # fetches user from database by email
            user = db.users.find_one({'email': email})

            # if user with provided email already exists in the database
            if user:
                flash('Email address already exists')  # render error message to be displayed
                return redirect(url_for('auth.signup'))  # redirects to sign up page

            # if provided email is available
            # insert to database with fields from form
            db.users.insert_one(
                {'email': email, 'name': name, 'password': generate_password_hash(password, method='sha256')})

            return redirect(url_for('auth.login'))  # redirects to login page
        else:  # if request method is GET
            return render_template('signup.html')  # renders sign up template


# logout method allows existing users to log out of the app
@auth.route('/logout')  # accepts GET requests at specified URL
@login_required  # only logged-in users allowed
def logout():  # no parameters needed
    logout_user()  # logs user out with LoginManager
    return redirect(url_for('main.index'))  # redirects to home page


# update method allows existing users to update the details of their own accounts
@auth.post('/user/<user_id>/update/')  # accepts POST requests at specified URL
@login_required  # only logged-in users allowed
def update(user_id):  # parameter user_id required
    if ObjectId(user_id) == current_user.id:  # if users are the same
        email = request.form.get('email')  # field 'email' from submitted form
        name = request.form.get('name')  # field 'name' from submitted form
        password = request.form.get('password')  # field 'password' from submitted form

        # if provided email is different from the current one, but is already in use by other user
        if current_user.email != email and db.users.find_one({'email': email}):
            flash('Email address already in use')  # renders error message to be displayed
            return redirect(url_for('main.profile'))  # redirects to profile page

        # if new email is available
        # update to database with fields from form
        db.users.update_one({"_id": current_user.id}, {"$set": {
            "email": email,
            "name": name,
            "password": generate_password_hash(password, method='sha256'),
        }})

    return redirect(url_for('main.profile'))  # redirects to profile page


# delete method allows existing users to delete their own accounts
@auth.post('/user/<user_id>/delete/')  # accepts POST requests at specified URL
@login_required  # only logged-in users allowed
def delete(user_id):  # parameter user_id required
    if ObjectId(user_id) == current_user.id:  # if users are the same
        # delete user from database by id
        db.users.delete_one({"_id": current_user.id})
        return logout()  # logs local instance of User out with local logout()

    return redirect(url_for('main.profile'))  # redirects to profile page
