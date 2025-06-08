import pytest

from app import app as flask_app
from extensions import db

@pytest.fixture
def client():
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    with flask_app.app_context():
        db.create_all()
    with flask_app.test_client() as client:
        yield client
    with flask_app.app_context():
        db.drop_all()
        db.session.remove()
