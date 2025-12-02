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

from models import User, Question, Answer


def register(client, username, email, password="password"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email, password="password"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_registration_and_login(client):
    register(client, "alice", "alice@example.com")
    user = User.query.filter_by(username="alice").first()
    assert user is not None

    login(client, "alice@example.com")
    resp = client.get("/dashboard", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Unanswered Questions" in resp.data


def test_dashboard_button_shows_unanswered_count(client):
    register(client, "alice", "alice@example.com")
    register(client, "bob", "bob@example.com")

    login(client, "bob@example.com")
    client.post(
        "/profile/alice",
        data={"question_text": "Hello Alice?", "anonymous": "y"},
        follow_redirects=True,
    )
    client.get("/logout", follow_redirects=True)

    login(client, "alice@example.com")
    resp = client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard - 1" in resp.data

    alice = User.query.filter_by(username="alice").first()
    question = Question.query.filter_by(receiver_id=alice.id).first()
    client.post(
        "/profile/alice",
        data={"question_id": question.id, "answer_text": "Answering now"},
        follow_redirects=True,
    )

    resp = client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard - 1" not in resp.data


def test_question_submission(client):
    register(client, "alice", "alice@example.com")
    register(client, "bob", "bob@example.com")

    login(client, "alice@example.com")
    client.post(
        "/profile/bob",
        data={"question_text": "Hello?", "anonymous": "y"},
        follow_redirects=True,
    )

    question = Question.query.first()
    assert question is not None
    assert question.receiver.username == "bob"
    assert question.sender.username == "alice"


def test_answer_flow(client):
    register(client, "alice", "alice@example.com")
    register(client, "bob", "bob@example.com")

    login(client, "alice@example.com")
    client.post(
        "/profile/bob",
        data={"question_text": "Question for Bob", "anonymous": "y"},
        follow_redirects=True,
    )
    client.get("/logout", follow_redirects=True)

    login(client, "bob@example.com")
    question = Question.query.first()
    client.post(
        "/profile/bob",
        data={"question_id": question.id, "answer_text": "42"},
        follow_redirects=True,
    )

    answer = Answer.query.first()
    assert answer is not None
    assert answer.question_id == question.id
    assert answer.author.username == "bob"


def test_update_account_info(client, monkeypatch):
    register(client, "alice", "alice@example.com")
    login(client, "alice@example.com")

    # Ensure avatar URL check passes during this test
    monkeypatch.setattr("forms._url_is_accessible", lambda url: True)
    monkeypatch.setattr("forms._fetch_image_size", lambda url: (100, 100))

    bio_text = "Hello there"
    avatar = "https://avatars.githubusercontent.com/u/1.png"
    client.post(
        "/dashboard",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "bio": bio_text,
            "avatar_url": avatar,
            "submit": "Update",
        },
        follow_redirects=True,
    )

    user = User.query.filter_by(username="alice").first()
    assert user.bio == bio_text
    assert user.avatar_url == avatar

    resp = client.get("/profile/alice", follow_redirects=True)
    assert bio_text.encode() in resp.data
    assert avatar.encode() in resp.data


def test_avatar_url_requires_image_extension(client):
    register(client, "eve", "eve@example.com")
    login(client, "eve@example.com")

    invalid_avatar = "https://avatars.githubusercontent.com/u/1.txt"
    client.post(
        "/dashboard",
        data={
            "username": "eve",
            "email": "eve@example.com",
            "avatar_url": invalid_avatar,
            "submit": "Update",
        },
        follow_redirects=True,
    )

    user = User.query.filter_by(username="eve").first()
    assert user.avatar_url is None


def test_avatar_url_must_be_accessible(client, monkeypatch):
    register(client, "tom", "tom@example.com")
    login(client, "tom@example.com")

    avatar = "https://avatars.githubusercontent.com/u/2.png"

    # Simulate inaccessible avatar URL
    monkeypatch.setattr("forms._url_is_accessible", lambda url: False)

    client.post(
        "/dashboard",
        data={
            "username": "tom",
            "email": "tom@example.com",
            "avatar_url": avatar,
            "submit": "Update",
        },
        follow_redirects=True,
    )

    user = User.query.filter_by(username="tom").first()
    assert user.avatar_url is None


def test_feed_order_and_content(client):
    """Feed should show recent answers in reverse order with question text and author link."""
    # Register two users
    register(client, "alice", "alice@example.com")
    register(client, "bob", "bob@example.com")

    # Alice asks Bob two questions
    login(client, "alice@example.com")
    client.post(
        "/profile/bob",
        data={"question_text": "First?", "anonymous": "y"},
        follow_redirects=True,
    )
    client.post(
        "/profile/bob",
        data={"question_text": "Second?", "anonymous": "y"},
        follow_redirects=True,
    )
    client.get("/logout", follow_redirects=True)

    # Bob answers the questions in order
    login(client, "bob@example.com")
    questions = Question.query.order_by(Question.created_at).all()
    client.post(
        "/profile/bob",
        data={"question_id": questions[0].id, "answer_text": "A1"},
        follow_redirects=True,
    )
    client.post(
        "/profile/bob",
        data={"question_id": questions[1].id, "answer_text": "A2"},
        follow_redirects=True,
    )

    # Fetch the public feed
    resp = client.get("/feed")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Ensure questions and author link are present
    assert "First?" in html
    assert "Second?" in html
    assert "/profile/bob" in html

    # Answers should be in reverse chronological order (A2 before A1)
    assert html.index("Second?") < html.index("First?")


def test_custom_404(client):
    resp = client.get('/nonexistent')
    assert resp.status_code == 404
    assert b"Oops! Page Not Found" in resp.data
