# Qbox, a Q&A website
# Copyright (C) 2025  Rhys Baker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        # Reset any cached engine/session that might point at a developer DB.
        db.session.remove()
        engines = db.engines
        if None in engines:
            engines[None].dispose()
        engines[None] = db.create_engine(flask_app.config['SQLALCHEMY_DATABASE_URI'])
        db.create_all()
    with flask_app.test_client() as client:
        yield client
    with flask_app.app_context():
        db.drop_all()
        db.session.remove()
