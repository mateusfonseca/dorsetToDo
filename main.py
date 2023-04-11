"""
This file defines the views for the app's main routes.
They are functions that respond to web requests with the appropriate web responses.
They invoke the templates that will be rendered in return (if applicable) and handle any errors
that may arise during the handling of the requests, as well as redirections.
"""

from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app import db

# creates blueprint for app's main routes
main = Blueprint('main', __name__)


# index method displays list of 'todos' from database and allows for the
# insertion of new ones
@main.route('/', methods=('GET', 'POST'))  # accepts GET and POST requests at specified URL
def index():  # no parameters needed
    if current_user.is_authenticated:  # if user is logged-in
        if request.method == 'POST':  # if request method is POST
            content = request.form.get('content')  # field 'content' from submitted form
            degree = request.form.get('degree')  # field 'degree' from submitted form
            # insert to database with fields from form
            db.todos.insert_one({'content': content, 'degree': degree, 'done': False, 'user_id': current_user.id})
            return redirect(url_for('main.index'))  # redirect to home page
        else:  # if request method is GET
            # fetch all 'todos' created by the user from database
            all_todos = db.todos.find({'user_id': current_user.id})
            return render_template('index.html', todos=list(all_todos))  # renders home template with list of todos
    else:  # if user is not logged-in
        if request.method == 'POST':  # if request method is POST
            return redirect(url_for('auth.login'))  # redirects to login page
        else:  # if request method is GET
            return render_template('index.html')  # renders home template


# update method allows the user to change the details of existing todos
@main.post('/todo/<todo_id>/update/')  # accepts POST requests at specified URL
@login_required  # only logged-in users allowed
def update(todo_id):  # parameter todo_id required
    # update to database with fields from form
    db.todos.update_one({"_id": ObjectId(todo_id)}, {"$set": {
        "content": request.form.get('content'),  # field 'content' from submitted form
        "degree": request.form.get('degree'),  # field 'degree' from submitted form
    }})

    return redirect(url_for('main.index'))  # redirects to home page


# done method allows the user to toggle existing todos' 'done' attribute
@main.post('/todo/<todo_id>/done/')  # accepts POST requests at specified URL
@login_required  # only logged-in users allowed
def done(todo_id):  # parameter todo_id required
    # fetch object from database by id
    todo = db.todos.find_one({"_id": ObjectId(todo_id)})
    # update to database toggling the 'done' attribute
    db.todos.update_one({"_id": ObjectId(todo_id)}, {"$set": {
        "done": not todo['done']
    }})

    return redirect(url_for('main.index'))  # redirects to home page


# delete method allows the user to delete existing todos
@main.post('/todo/<todo_id>/delete/')  # accepts POST requests at specified URL
@login_required  # only logged-in users allowed
def delete(todo_id):  # parameter todo_id required
    # delete object from database
    db.todos.delete_one({"_id": ObjectId(todo_id)})
    return redirect(url_for('main.index'))  # redirects to home page


# profile method allows the user to view their account details
@main.route('/profile')  # accepts GET requests at specified URL
@login_required  # only logged-in users allowed
def profile():  # no parameters needed
    return render_template('profile.html', user=current_user)  # renders profile template with current user
