'''
Filename: conftest.py
Path: ./tests/
Created Date: Monday, April 25rd 2022, 10:41:08 am
Author: Baptiste Bergmann
'''

import os
import pytest
from src.app import create_app
from src.dbHandler import init_db


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    os.remove("./database.db")
    with app.app_context():
        init_db()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()