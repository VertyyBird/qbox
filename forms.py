from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from urllib.parse import urlparse
from models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    bio = TextAreaField('Bio')
    avatar_url = StringField('Avatar URL')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

    def validate_avatar_url(self, avatar_url):
        if avatar_url.data:
            host = urlparse(avatar_url.data).netloc.lower()
            allowed_hosts = [
                'imgur.com', 'i.imgur.com', 'ibb.co', 'i.ibb.co',
                'github.com', 'raw.githubusercontent.com',
                'avatars.githubusercontent.com', 'user-images.githubusercontent.com',
            ]
            if not any(host.endswith(h) for h in allowed_hosts):
                raise ValidationError('Avatar URL host not allowed.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Your Question', validators=[DataRequired()])
    anonymous = BooleanField('Ask Anonymously')
    submit = SubmitField('Submit')

class AnswerForm(FlaskForm):
    answer_text = TextAreaField('Your Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    bio = TextAreaField('Bio')
    avatar_url = StringField('Avatar URL')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered.')

    def validate_avatar_url(self, avatar_url):
        if avatar_url.data:
            host = urlparse(avatar_url.data).netloc.lower()
            allowed_hosts = [
                'imgur.com', 'i.imgur.com', 'ibb.co', 'i.ibb.co',
                'github.com', 'raw.githubusercontent.com',
                'avatars.githubusercontent.com', 'user-images.githubusercontent.com',
            ]
            if not any(host.endswith(h) for h in allowed_hosts):
                raise ValidationError('Avatar URL host not allowed.')
