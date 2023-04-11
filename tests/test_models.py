"""
This file defines tests for the models of the app.
Each test is a function that interacts with a certain model and evaluates its parameters
against a pre-defined assertion. If the assertion is correct, the test has passed.
If the assertion is incorrect, the test has failed.
Each test tests only one parameter of the model, for this reason, tests are grouped
together into classes. Each class represents a suite of tests for a particular model.
"""

from werkzeug.security import generate_password_hash

from app import db
from models import User


class TestUserModel:  # user model test suite
    user = None  # user model to be used in all test cases
    email = 'pytest@email.com'  # dummy email for testing
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

    def test_is_active(self):  # instantiated user should be active
        assert self.user.is_active is True  # expects it to be true

    def test_is_authenticated(self):  # instantiated user should be authenticated
        assert self.user.is_authenticated is True  # expects it to be true

    def test_is_anonymous(self):  # instantiated user should not be anonymous
        assert self.user.is_anonymous is False  # expects it to be false

    def test_get_id(self):  # instantiated user should correctly return its id string
        assert self.user.get_id() == str(self.user.id)  # expects it to be the same
