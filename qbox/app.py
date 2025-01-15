from flask import Flask, render_template, url_for, flash, redirect, request
from extensions import db, migrate
from forms import RegistrationForm, LoginForm, QuestionForm, AnswerForm
from models import User, Question, Answer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@app.template_filter('time_since')
def time_since(dt):
    now = datetime.utcnow()
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

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
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
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    question_form = QuestionForm()
    answer_form = AnswerForm()
    if question_form.validate_on_submit():
        sender_id = None if question_form.anonymous.data else current_user.id
        question = Question(sender_id=sender_id, receiver_id=user.id, question_text=question_form.question_text.data)
        db.session.add(question)
        db.session.commit()
        flash('Your question has been submitted!', 'success')
        return redirect(url_for('profile', username=username))
    if answer_form.validate_on_submit():
        question_id = request.form.get('question_id')
        question = Question.query.get(question_id)
        if question and not question.answers:
            answer = Answer(question_id=question.id, author_id=current_user.id, answer_text=answer_form.answer_text.data)
            db.session.add(answer)
            db.session.commit()
            flash('Your answer has been submitted!', 'success')
            return redirect(url_for('profile', username=username))
    return render_template('profile.html', user=user, question_form=question_form, answer_form=answer_form)

@app.route('/dashboard')
@login_required
def dashboard():
    unanswered_questions = Question.query.filter_by(receiver_id=current_user.id).filter(~Question.answers.any()).all()
    answer_form = AnswerForm()
    return render_template('dashboard.html', unanswered_questions=unanswered_questions, answer_form=answer_form)

if __name__ == "__main__":
    app.run(debug=True)