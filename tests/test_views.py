"""
This file defines tests for the views of the app.
Each test is a function that interacts with a certain view and evaluates its response
against a pre-defined assertion. If the assertion is correct, the test has passed.
If the assertion is incorrect, the test has failed.
Each test tests only one functionality of the view, for this reason, tests are grouped
together into classes. Each class represents a suite of tests for a particular view.
"""

from flask import url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import User


class TestMainView:  # main view test suite
    user = None  # user model to be used in all test cases
    email = 'pytest@email.com'  # dummy email for testing
    name = 'pytest'  # dummy name for testing
    password = 'pytest123'  # dummy password for testing

    todo = None  # to-do model to be used in all test cases
    content = 'pytest to-do'  # dummy content for testing
    degree = 'Important'  # dummy degree for testing
    content_updated = 'pytest to-do later'  # dummy updated content for testing
    degree_updated = 'Unimportant'  # dummy updated degree for testing

    @classmethod
    def setup_class(cls):  # prepares parameters that will be shared by the test cases
        # inserts mock user to the database
        db.users.insert_one({
            'email': cls.email,
            'name': cls.name,
            'password': generate_password_hash(cls.password, method='sha256')
        })
        cls.user = User(db.users.find_one({'email': cls.email}))  # fetches mock user from the database

        # inserts mock to-do to the database
        db.todos.insert_one({
            'content': cls.content,
            'degree': cls.degree,
            'done': False,
            'user_id': cls.user.id
        })
        cls.todo = db.todos.find_one({'user_id': cls.user.id})  # fetches mock to-do from the database

    @classmethod
    def teardown_class(cls):  # clean up/reset resources previously created after all test cases are finished
        db.users.delete_one({"_id": cls.user.id})  # deletes mock user from the database
        db.todos.delete_many({"user_id": cls.user.id})  # deletes all mock to-dos from the database

    # unauthenticated GET to index should NOT display list of to-dos
    def test_get_index_unauthenticated(self, client, context):
        with context:
            response = client.get(url_for('main.index'))  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Start using' in response.text  # expects correct template to be rendered

    # authenticated GET to index should display list of to-dos
    def test_get_index_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            response = client.get(url_for('main.index'))  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

    # unauthenticated POST to index should NOT add new to-do
    def test_post_index_unauthenticated(self, client, context):
        with context:
            # sends POST request to view with form
            response = client.post(url_for('main.index'), data={'content': self.content, 'degree': self.degree},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered
            assert len(list(db.todos.find({'user_id': self.user.id}))) < 2  # expects new to-do to NOT have been added

    # authenticated POST to index should add new to-do
    def test_post_index_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view with form
            response = client.post(url_for('main.index'), data={'content': self.content, 'degree': self.degree},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

            todo = db.todos.find({'user_id': self.user.id})[1]  # fetches new to-do from database
            assert todo['content'] == self.content  # expects database value to match local value
            assert todo['degree'] == self.degree  # expects database value to match local value

    # unauthenticated POST to update should NOT change the object's attributes
    def test_post_update_unauthenticated(self, client, context):
        with context:
            # sends POST request to view with form
            response = client.post(url_for('main.update', todo_id=self.todo['_id']),
                                   data={'content': self.content_updated, 'degree': self.degree_updated},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered

            todo = db.todos.find_one({'_id': self.todo['_id']})  # fetches to-do from database
            assert todo['content'] == self.content  # expects database value to NOT have changed
            assert todo['degree'] == self.degree  # expects database value to NOT have changed

    # authenticated POST to update should change the object's attributes
    def test_post_update_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view with form
            response = client.post(url_for('main.update', todo_id=self.todo['_id']),
                                   data={'content': self.content_updated, 'degree': self.degree_updated},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

            todo = db.todos.find_one({'_id': self.todo['_id']})  # fetches to-do from database
            assert todo['content'] == self.content_updated  # expects database value to have changed
            assert todo['degree'] == self.degree_updated  # expects database value to have changed

    # unauthenticated POST to done should NOT toggle the object's 'done' attribute
    def test_post_done_unauthenticated(self, client, context):
        with context:
            # sends POST request to view
            response = client.post(url_for('main.done', todo_id=self.todo['_id']), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered
            # expects database value to NOT have changed
            assert db.todos.find_one({'_id': self.todo['_id']})['done'] is self.todo['done']

    # authenticated POST to done should toggle the object's 'done' attribute
    def test_post_done_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view
            response = client.post(url_for('main.done', todo_id=self.todo['_id']), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered
            # expects database value to have changed
            assert db.todos.find_one({'_id': self.todo['_id']})['done'] is not self.todo['done']

    # unauthenticated POST to delete should NOT delete object
    def test_post_delete_unauthenticated(self, client, context):
        with context:
            # sends POST request to view
            response = client.post(url_for('main.delete', todo_id=self.todo['_id']), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered
            assert db.todos.find_one({'_id': self.todo['_id']}) is not None  # expects to-do to NOT have been deleted

    # authenticated POST to delete should delete object
    def test_post_delete_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view
            response = client.post(url_for('main.delete', todo_id=self.todo['_id']), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered
            assert db.todos.find_one({'_id': self.todo['_id']}) is None  # expects to-do to have been deleted

    # unauthenticated GET to profile should NOT display account details
    def test_get_profile_unauthenticated(self, client, context):
        with context:
            response = client.get(url_for('main.profile'), follow_redirects=True)  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered

    # authenticated GET to profile should display account details
    def test_get_profile_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            response = client.get(url_for('main.profile'))  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.profile')  # expects correct redirection
            assert '<h3 class="title">Account Details' in response.text  # expects correct template to be rendered


class TestAuthView:  # auth view test suite
    user = None  # user model to be used in all test cases
    email = 'pytest@email.com'  # dummy email for testing
    other_email = 'other_pytest@email.com'  # dummy other email for testing
    name = 'pytest'  # dummy name for testing
    password = 'pytest123'  # dummy password for testing

    @classmethod
    def setup_class(cls):  # prepares parameters that will be shared by the test cases
        # inserts mock user to the database
        db.users.insert_one({
            'email': cls.email,
            'name': cls.name,
            'password': generate_password_hash(cls.password, method='sha256')
        })
        cls.user = User(db.users.find_one({'email': cls.email}))  # fetches mock user from the database

    @classmethod
    def teardown_class(cls):  # clean up/reset resources previously created after all test cases are finished
        db.users.delete_one({"_id": cls.user.id})  # deletes mock user from the database
        db.users.delete_one({"email": cls.other_email})  # deletes other mock user from the database

    # unauthenticated GET to 'login' should display login page
    def test_get_login_unauthenticated(self, client, context):
        with context:
            response = client.get(url_for('auth.login'))  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered

    # authenticated GET to 'login' should redirect to home page
    def test_get_login_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            response = client.get(url_for('auth.login'), follow_redirects=True)  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

    # unauthenticated POST to 'login' should display error message if credentials are invalid or
    # redirect to home page if credentials are valid
    def test_post_login_unauthenticated(self, client, context):
        with context:
            # sends POST request to view with form
            response = client.post(url_for('auth.login'), data={'email': 'fail@email.com', 'password': 'fail123'},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            # expects correct template to be rendered
            assert 'Please check your login details and try again.' in response.text

            # sends POST request to view with form
            response = client.post(url_for('auth.login'), data={'email': self.email, 'password': self.password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

    # authenticated POST to 'login' should redirect to home page
    def test_post_login_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view with form
            response = client.post(url_for('auth.login'), data={'email': self.email, 'password': self.password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

    # unauthenticated GET to 'signup' should display sign up page
    def test_get_signup_unauthenticated(self, client, context):
        with context:
            response = client.get(url_for('auth.signup'))  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.signup')  # expects correct redirection
            assert '<h3 class="title">Sign Up' in response.text  # expects correct template to be rendered

    # authenticated GET to 'signup' should redirect to home page
    def test_get_signup_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            response = client.get(url_for('auth.signup'), follow_redirects=True)  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered

    # unauthenticated POST to 'signup' should display error message if email is already in use or
    # add new user if email is available
    def test_post_signup_unauthenticated(self, client, context):
        with context:
            # sends POST request to view with form
            response = client.post(url_for('auth.signup'),
                                   data={'email': self.email, 'name': self.name, 'password': self.password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.signup')  # expects correct redirection
            assert 'Email address already exists' in response.text  # expects correct template to be rendered
            # expects new user with same email to NOT have been added
            assert len(list(db.users.find({'email': self.email}))) == 1

            # sends POST request to view with form
            response = client.post(url_for('auth.signup'),
                                   data={'email': self.other_email, 'name': self.name, 'password': self.password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered
            # expects new user with different email to have been added
            assert db.users.find_one({'email': self.other_email}) is not None

    # authenticated POST to 'signup' should redirect to home page
    def test_post_signup_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view with form
            response = client.post(url_for('auth.signup'),
                                   data={'email': self.email, 'name': self.name, 'password': self.password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Dorset To-Do List' in response.text  # expects correct template to be rendered
            # expects new user with same email to NOT have been added
            assert len(list(db.users.find({'email': self.email}))) == 1

    # unauthenticated GET to 'logout' should redirect to login page
    def test_get_logout_unauthenticated(self, client, context):
        with context:
            response = client.get(url_for('auth.logout'), follow_redirects=True)  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered

    # authenticated GET to 'logout' should log user out and redirect to home page
    def test_get_logout_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            response = client.get(url_for('auth.logout'), follow_redirects=True)  # sends GET request to view
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Start using' in response.text  # expects correct template to be rendered

    # unauthenticated POST to 'update' should redirect to login page
    def test_post_update_unauthenticated(self, client, context):
        with context:
            new_email = 'new_pytest@email.com'  # dummy new email for testing
            new_name = 'new_pytest'  # dummy new name for testing
            new_password = 'new_pytest123'  # dummy new password for testing

            # sends POST request to view with form
            response = client.post(url_for('auth.update', user_id=self.user.id),
                                   data={'email': new_email, 'name': new_name, 'password': new_password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered

            user = db.users.find_one({'_id': self.user.id})  # fetches mock user from the database
            assert user['email'] == self.email and user['email'] != new_email  # expects it NOT to have changed
            assert user['name'] == self.name and user['name'] != new_name  # expects it NOT to have changed
            # expects it NOT to have changed
            assert check_password_hash(user['password'], self.password) and not check_password_hash(user['password'],
                                                                                                    new_password)

    # authenticated POST to 'update' should make changes to database and redirect to profile page
    def test_post_update_authenticated(self, client, context):
        with context:
            new_email = 'new_pytest@email.com'  # dummy new email for testing
            new_name = 'new_pytest'  # dummy new name for testing
            new_password = 'new_pytest123'  # dummy new password for testing

            login_user(self.user)  # logs-in in mock user
            # sends POST request to view with form
            response = client.post(url_for('auth.update', user_id=self.user.id),
                                   data={'email': new_email, 'name': new_name, 'password': new_password},
                                   follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.profile')  # expects correct redirection
            assert '<h3 class="title">Account Details' in response.text  # expects correct template to be rendered

            user = db.users.find_one({'_id': self.user.id})  # fetches mock user from the database
            assert user['email'] != self.email and user['email'] == new_email  # expects it to have changed
            assert user['name'] != self.name and user['name'] == new_name  # expects it to have changed
            # expects it to have changed
            assert not check_password_hash(user['password'], self.password) and check_password_hash(user['password'],
                                                                                                    new_password)

    # unauthenticated POST to 'delete' should redirect to login page
    def test_post_delete_unauthenticated(self, client, context):
        with context:
            # sends POST request to view
            response = client.post(url_for('auth.delete', user_id=self.user.id), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('auth.login')  # expects correct redirection
            assert '<h3 class="title">Login' in response.text  # expects correct template to be rendered
            assert db.users.find_one({'_id': self.user.id}) is not None  # expects it NOT to have been deleted

    # authenticated POST to 'delete' should make changes to database and redirect to home page
    def test_post_delete_authenticated(self, client, context):
        with context:
            login_user(self.user)  # logs-in in mock user
            # sends POST request to view
            response = client.post(url_for('auth.delete', user_id=self.user.id), follow_redirects=True)
            assert response.status_code == 200  # expects request to be successful
            assert response.request.path == url_for('main.index')  # expects correct redirection
            assert '<h3 class="title">Start using' in response.text  # expects correct template to be rendered
            assert db.users.find_one({'_id': self.user.id}) is None  # expects it to have been deleted
