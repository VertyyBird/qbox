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
