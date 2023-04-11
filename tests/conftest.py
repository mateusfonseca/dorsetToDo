"""
This file defines the test settings for the project.
Tests are run using the pytest framework and library.
"""

import pytest

from app import create_app


@pytest.fixture()  # marks method as a fixture that can be reused by various test cases
def app():  # instance of app to be tested
    app = create_app()  # instantiates a test app with same settings as the regular app
    # add the TESTING flag to this instance
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here, if necessary

    yield app  # makes it available to the caller before ending execution

    # clean up / reset resources here, if necessary


@pytest.fixture()  # marks method as a fixture that can be reused by various test cases
def client(app):  # defines a client for simulating HTTP requests
    return app.test_client()  # returns client


@pytest.fixture()  # marks method as a fixture that can be reused by various test cases
def context(app):  # defines a context for the requests that will be simulated
    return app.test_request_context()  # returns context
