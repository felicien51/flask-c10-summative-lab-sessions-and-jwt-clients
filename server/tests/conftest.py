import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app as flask_app
from config import db as _db


@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
