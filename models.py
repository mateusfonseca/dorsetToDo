"""
This file defines the models that reflect the database's entities.
Each class is an entity and their properties are the tables' columns.
Instances of these classes are the database's entries, the tables' rows.
"""

from bson import ObjectId
from flask_login import UserMixin


class User(UserMixin):  # app's user
    def __init__(self, user):  # instantiates User with details from JSON-like model from MongoDB
        self.id = ObjectId(user['_id'])  # user's id
        self.email = user['email']  # user's email
        self.name = user['name']  # user's name
        self.password = user['password']  # user's password

    """
    The following properties are inherited from UserMixin as they are required by Flask-Login:
    
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None
    """
