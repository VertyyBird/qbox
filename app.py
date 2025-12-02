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

from flask import Flask, render_template, url_for, flash, redirect, request, abort
from markupsafe import Markup, escape
from extensions import db, migrate
from forms import RegistrationForm, LoginForm, QuestionForm, AnswerForm, UpdateAccountForm
from models import User, Question, Answer, utcnow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import secrets

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    if os.getenv('FLASK_ENV') == 'production':
        raise RuntimeError('SECRET_KEY not set; define it in your environment or .env')
    secret_key = secrets.token_hex(16)
    print('Warning: SECRET_KEY not set; generated a temporary key for development.')

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///qbox.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_now():
    unanswered_count = 0
    if current_user.is_authenticated:
        unanswered_count = (
            Question.query
            .filter_by(receiver_id=current_user.id)
            .filter(~Question.answers.any())
            .count()
        )
    return {'now': utcnow, 'unanswered_count': unanswered_count}

@app.template_filter('time_since')
def time_since(dt):
    # Normalize to timezone-aware UTC to avoid naive/aware conflicts.
    if dt is None:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = utcnow()
    diff = now - dt
    if diff < timedelta(hours=24):
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        if hours > 0:
            return f'{hours} hours ago'
        elif minutes > 0:
            return f'{minutes} minutes ago'
        else:
            return 'just now'
    else:
        if dt.year == now.year:
            return dt.strftime('%I:%M %p %d %b')
        else:
            return dt.strftime('%I:%M %p %d %b %y')

@app.template_filter('nl2br')
def nl2br(value):
    """Escape text and convert newlines to ``<br>`` tags."""
    if value is None:
        return ''
    escaped = escape(value)
    return Markup(escaped.replace('\n', Markup('<br>')))

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/feed')
def feed():
    """Public feed showing recent answers."""
    page = request.args.get('page', 1, type=int)
    answers = (
        Answer.query
        .order_by(Answer.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template('feed.html', answers=answers)

@app.route('/profile/<username>/a/<public_id>')
def answer_permalink(username, public_id):
    """Show a single answer permalinked by its public ID."""
    user = User.query.filter_by(username=username).first_or_404()
    answer = Answer.query.filter_by(public_id=public_id, author_id=user.id).first_or_404()
    return render_template('answer.html', user=user, answer=answer)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                bio=form.bio.data,
                avatar_url=form.avatar_url.data,
            )
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            print(f'Error: {str(e)}')  # Print the error to the console for debugging
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('profile', username=user.username))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('home'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    question_form = QuestionForm()
    answer_form = AnswerForm()
    if question_form.validate_on_submit():
        ip_address = (
            request.access_route[0]
            if request.access_route
            else request.remote_addr
        ) or '0.0.0.0'
        if current_user.is_authenticated:
            sender_id = current_user.id
            is_anonymous = question_form.anonymous.data
        else:
            sender_id = None
            is_anonymous = True
        question = Question(
            sender_id=sender_id,
            receiver_id=user.id,
            is_anonymous=is_anonymous,
            question_text=question_form.question_text.data,
            ip_address=ip_address,
        )
        db.session.add(question)
        db.session.commit()
        flash('Your question has been submitted!', 'success')
        return redirect(url_for('profile', username=username))
    if answer_form.validate_on_submit():
        if not current_user.is_authenticated or current_user.id != user.id:
            abort(403)
        question_id = request.form.get('question_id', type=int)
        question = Question.query.filter_by(id=question_id, receiver_id=user.id).first()
        if not question:
            abort(404)
        if not question.answers:
            answer = Answer(question_id=question.id, author_id=current_user.id, answer_text=answer_form.answer_text.data)
            db.session.add(answer)
            db.session.commit()
            flash('Your answer has been submitted!', 'success')
            return redirect(url_for('profile', username=username))
    answers = Answer.query.filter_by(author_id=user.id).order_by(Answer.created_at.desc()).all()
    return render_template('profile.html', user=user, question_form=question_form, answer_form=answer_form, answers=answers)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    unanswered_questions = (
        Question.query
        .filter_by(receiver_id=current_user.id)
        .filter(~Question.answers.any())
        .order_by(Question.created_at.desc())
        .all()
    )
    answer_form = AnswerForm()
    update_form = UpdateAccountForm()

    if update_form.submit.data and update_form.validate_on_submit():
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        current_user.bio = update_form.bio.data
        current_user.avatar_url = update_form.avatar_url.data
        if update_form.password.data:
            current_user.password_hash = generate_password_hash(update_form.password.data)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email
        update_form.bio.data = current_user.bio
        update_form.avatar_url.data = current_user.avatar_url

    return render_template('dashboard.html', unanswered_questions=unanswered_questions,
                           answer_form=answer_form, update_form=update_form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
