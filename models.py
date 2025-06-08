from datetime import datetime
from extensions import db  # Import db from extensions
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """
    User Model
    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for the user, maximum length of 80 characters.
        email (str): Unique email address for the user, maximum length of 120 characters.
        password_hash (str): Hashed password for the user, maximum length of 128 characters.
        created_at (datetime): Timestamp when the user was created, defaults to the current UTC time.
    Methods:
        __repr__(): Returns a string representation of the user instance.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='receiver', lazy=True, foreign_keys='Question.receiver_id')
    answers = db.relationship('Answer', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    question_text = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # New field for IP address
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_questions')
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.id}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Answer {self.id}>'
