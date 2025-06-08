from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler, URLError
from urllib.error import HTTPError
from models import User
from flask_login import current_user
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent / "config"

def _load_allowed_hosts():
    path = CONFIG_DIR / "avatar_hosts.txt"
    if path.exists():
        with path.open() as f:
            return [line.strip() for line in f if line.strip()]
    return []

ALLOWED_AVATAR_HOSTS = _load_allowed_hosts()
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _url_is_accessible(url: str) -> bool:
    """Return True if the url responds with a successful non-redirect status."""
    class _NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

        def http_error_302(self, req, fp, code, msg, headers):
            raise HTTPError(req.full_url, code, msg, headers, fp)

        http_error_301 = http_error_302
        http_error_303 = http_error_302
        http_error_307 = http_error_302
        http_error_308 = http_error_302

    opener = build_opener(_NoRedirect())
    request = Request(url, method="HEAD")
    try:
        with opener.open(request, timeout=5) as resp:
            return 200 <= resp.status < 300
    except HTTPError as e:
        return False
    except URLError:
        return False

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
            parsed = urlparse(avatar_url.data)
            host = parsed.netloc.lower()
            if not any(host.endswith(h) for h in ALLOWED_AVATAR_HOSTS):
                raise ValidationError('Avatar URL host not allowed.')
            path = parsed.path.lower()
            if not any(path.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
                raise ValidationError('Avatar URL must end with an image file extension.')
            if not _url_is_accessible(avatar_url.data):
                raise ValidationError('Avatar URL is not accessible or redirects.')

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
            parsed = urlparse(avatar_url.data)
            host = parsed.netloc.lower()
            if not any(host.endswith(h) for h in ALLOWED_AVATAR_HOSTS):
                raise ValidationError('Avatar URL host not allowed.')
            path = parsed.path.lower()
            if not any(path.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
                raise ValidationError('Avatar URL must end with an image file extension.')
            if not _url_is_accessible(avatar_url.data):
                raise ValidationError("Avatar URL is not accessible or redirects.")

