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
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
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
