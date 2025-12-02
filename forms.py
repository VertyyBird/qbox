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

import struct
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, URLError, build_opener

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from models import User

CONFIG_DIR = Path(__file__).resolve().parent / "config"

def _load_allowed_hosts():
    path = CONFIG_DIR / "avatar_hosts.txt"
    if path.exists():
        with path.open() as f:
            return [line.strip() for line in f if line.strip()]
    return []

ALLOWED_AVATAR_HOSTS = _load_allowed_hosts()
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
AVATAR_RENDER_SIZE_PX = 100
MAX_AVATAR_DIMENSION = AVATAR_RENDER_SIZE_PX * 3
IMAGE_PROBE_MAX_BYTES = 65536


def _url_is_accessible(url: str) -> bool:
    """Return True if the url responds with a 2xx status after following at most one redirect."""
    def _host_allowed(target_url: str) -> bool:
        target_host = urlparse(target_url).netloc.lower()
        return any(target_host.endswith(h) for h in ALLOWED_AVATAR_HOSTS)

    def _try_request(method: str) -> bool:
        req = Request(url, method=method)
        try:
            with build_opener().open(req, timeout=5) as resp:
                final_url = resp.geturl()
                if not _host_allowed(final_url):
                    return False
                return 200 <= resp.status < 300
        except HTTPError as e:
            # Accept a redirect or a HEAD-not-allowed by retrying with GET.
            if e.code in {301, 302, 303, 307, 308, 405} and method == "HEAD":
                return _try_request("GET")
            return False
        except URLError:
            return False

    return _try_request("HEAD")


def _probe_image_size(data: bytes):
    """Return (width, height) for basic image types using only header bytes."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data.startswith(b"\xff\xd8"):
        idx = 2
        data_len = len(data)
        while idx + 9 <= data_len:
            if data[idx] != 0xFF:
                break
            marker = data[idx + 1]
            if marker == 0xDA:  # Start of scan
                break
            if data_len < idx + 4:
                break
            seg_length = struct.unpack(">H", data[idx + 2:idx + 4])[0]
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if idx + 5 + 4 <= data_len:
                    height, width = struct.unpack(">HH", data[idx + 5:idx + 9])
                    return width, height
                break
            idx += 2 + seg_length
    return None


def _fetch_image_size(url: str):
    """Fetch the remote image (limited bytes) and return (w, h) if detectable."""
    req = Request(url, method="GET")
    try:
        with build_opener().open(req, timeout=5) as resp:
            data = resp.read(IMAGE_PROBE_MAX_BYTES)
            return _probe_image_size(data)
    except Exception:
        return None


def _image_within_render_bounds(url: str, max_dimension: int = MAX_AVATAR_DIMENSION) -> bool:
    size = _fetch_image_size(url)
    if not size:
        return False
    width, height = size
    return width <= max_dimension and height <= max_dimension

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
            if not _image_within_render_bounds(avatar_url.data):
                raise ValidationError(f'Avatar image must be at most {MAX_AVATAR_DIMENSION}x{MAX_AVATAR_DIMENSION} pixels.')

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
            if not _image_within_render_bounds(avatar_url.data):
                raise ValidationError(f'Avatar image must be at most {MAX_AVATAR_DIMENSION}x{MAX_AVATAR_DIMENSION} pixels.')


class ModerateQuestionForm(FlaskForm):
    question_id = HiddenField(validators=[DataRequired()])
    action = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Confirm')
