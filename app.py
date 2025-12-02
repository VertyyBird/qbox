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
from forms import RegistrationForm, LoginForm, QuestionForm, AnswerForm, UpdateAccountForm, ModerateQuestionForm, AnswerReportForm, BlockForm
from models import User, Question, Answer, AnswerReport, Block, utcnow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
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
if os.getenv('FLASK_ENV') == 'production':
    # Lock down host/canonical scheme in production.
    app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', None)
    app.config['PREFERRED_URL_SCHEME'] = 'https'

db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Respect proxy headers for correct URL generation in production.
if os.getenv('FLASK_ENV') == 'production':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

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


def _active_block_for(user_id, ip_address):
    now = utcnow()
    blocks = Block.query.filter_by(active=True).all()
    matched = None
    for block in blocks:
        if block.expires_at and block.expires_at <= now:
            block.active = False
            continue
        if block.user_id and user_id and block.user_id == user_id:
            matched = block
            break
        if block.ip_address and ip_address and block.ip_address == ip_address:
            matched = block
            break
    db.session.commit()
    return matched

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/feed')
def feed():
    """Public feed showing recent answers."""
    page = request.args.get('page', 1, type=int)
    user_page = request.args.get('users', 1, type=int)
    answers = (
        Answer.query
        .order_by(Answer.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    new_users = (
        User.query
        .order_by(User.created_at.desc())
        .paginate(page=user_page, per_page=10, error_out=False)
    )
    report_form = AnswerReportForm()
    return render_template('feed.html', answers=answers, new_users=new_users, report_form=report_form)

@app.route('/user/<username>/a/<public_id>')
def answer_permalink(username, public_id):
    """Show a single answer permalinked by its public ID."""
    user = User.query.filter_by(username=username).first_or_404()
    answer = Answer.query.filter_by(public_id=public_id, author_id=user.id).first_or_404()
    report_form = AnswerReportForm()
    return render_template('answer.html', user=user, answer=answer, report_form=report_form)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/answers/<int:answer_id>/report', methods=['POST'])
def report_answer(answer_id):
    form = AnswerReportForm()
    if not form.validate_on_submit() or int(form.answer_id.data) != answer_id:
        abort(400)
    answer = Answer.query.get_or_404(answer_id)
    reporter_ip = (request.access_route[0] if request.access_route else request.remote_addr) or '0.0.0.0'
    report = AnswerReport(
        answer_id=answer.id,
        reporter_user_id=current_user.id if current_user.is_authenticated else None,
        reporter_ip=reporter_ip,
        reason=form.reason.data,
    )
    db.session.add(report)
    db.session.commit()
    flash('Answer reported for review.', 'success')
    return redirect(request.referrer or url_for('answer_permalink', username=answer.author.username, public_id=answer.public_id))

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

@app.route('/user/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    question_form = QuestionForm()
    answer_form = AnswerForm()
    report_form = AnswerReportForm()
    if question_form.validate_on_submit():
        # Simple per-IP rate limit: max 5 questions per minute per receiver.
        ip_address = (
            request.access_route[0]
            if request.access_route
            else request.remote_addr
        ) or '0.0.0.0'
        block = _active_block_for(current_user.id if current_user.is_authenticated else None, ip_address)
        if block:
            flash('You are blocked from submitting questions at this time.', 'danger')
            return redirect(url_for('profile', username=username))
        recent_window = utcnow() - timedelta(minutes=1)
        recent_count = (
            Question.query
            .filter_by(receiver_id=user.id, ip_address=ip_address)
            .filter(Question.created_at >= recent_window)
            .count()
        )
        if recent_count >= 5:
            flash('You are sending questions too quickly. Please wait a moment and try again.', 'danger')
            return redirect(url_for('profile', username=username))
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
    return render_template('profile.html', user=user, question_form=question_form, answer_form=answer_form, answers=answers, report_form=report_form)

@app.route('/profile/<username>')
def legacy_profile(username):
    return redirect(url_for('profile', username=username), code=301)

@app.route('/profile/<username>/a/<public_id>')
def legacy_answer_permalink(username, public_id):
    return redirect(url_for('answer_permalink', username=username, public_id=public_id), code=301)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    unanswered_questions = (
        Question.query
        .filter_by(receiver_id=current_user.id)
        .filter(~Question.answers.any())
        .filter_by(is_hidden=False)
        .order_by(Question.created_at.desc())
        .all()
    )
    answer_form = AnswerForm()
    moderate_form = ModerateQuestionForm()
    return render_template('dashboard.html', unanswered_questions=unanswered_questions,
                           answer_form=answer_form, moderate_form=moderate_form)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
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
        return redirect(url_for('settings'))

    if request.method == 'GET':
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email
        update_form.bio.data = current_user.bio
        update_form.avatar_url.data = current_user.avatar_url

    return render_template('settings.html', update_form=update_form)


@app.route('/questions/<int:question_id>/moderate', methods=['POST'])
@login_required
def moderate_question(question_id):
    form = ModerateQuestionForm()
    if not form.validate_on_submit() or int(form.question_id.data) != question_id:
        abort(400)
    question = Question.query.get_or_404(question_id)
    if question.receiver_id != current_user.id:
        abort(403)
    action = form.action.data
    if action == 'hide':
        question.is_hidden = True
        flash('Question hidden.', 'success')
    elif action == 'flag':
        question.is_flagged = True
        question.is_hidden = True
        flash('Question flagged and hidden.', 'success')
        # Auto-block anonymous IP if repeatedly flagged.
        if not question.sender_id:
            flagged_count = Question.query.filter_by(ip_address=question.ip_address, is_flagged=True).count()
            if flagged_count >= 5 and not _active_block_for(None, question.ip_address):
                auto_block = Block(
                    ip_address=question.ip_address,
                    reason='Auto-blocked after repeated flags',
                    expires_at=utcnow() + timedelta(days=30),
                    active=True,
                )
                db.session.add(auto_block)
    else:
        abort(400)
    db.session.commit()
    return redirect(url_for('dashboard'))


def _admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@app.route('/admin/moderation', methods=['GET'])
def admin_panel():
    _admin_required()
    block_form = BlockForm()
    alerts = []
    flagged_user_counts = (
        db.session.query(Question.sender_id, db.func.count(Question.id))
        .filter(Question.is_flagged.is_(True), Question.sender_id.isnot(None))
        .group_by(Question.sender_id)
        .all()
    )
    flagged_ip_counts = (
        db.session.query(Question.ip_address, db.func.count(Question.id))
        .filter(Question.is_flagged.is_(True))
        .group_by(Question.ip_address)
        .all()
    )
    for uid, count in flagged_user_counts:
        if uid and count >= 5:
            alerts.append(f'User ID {uid} has {count} flagged questions.')
    for ip, count in flagged_ip_counts:
        if ip and count >= 5:
            alerts.append(f'IP {ip} has {count} flagged questions.')

    flagged_questions = Question.query.filter_by(is_flagged=True).order_by(Question.created_at.desc()).all()
    answer_reports = AnswerReport.query.filter_by(resolved=False).order_by(AnswerReport.created_at.desc()).all()
    blocks = Block.query.order_by(Block.created_at.desc()).all()

    return render_template('admin.html', flagged_questions=flagged_questions,
                           answer_reports=answer_reports, blocks=blocks,
                           alerts=alerts, block_form=block_form)

@app.route('/admin/reports/<int:report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    _admin_required()
    report = AnswerReport.query.get_or_404(report_id)
    report.resolved = True
    db.session.commit()
    flash('Report resolved.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/blocks', methods=['POST'])
def create_block():
    _admin_required()
    form = BlockForm()
    if not form.validate_on_submit():
        abort(400)
    expires_at = None
    if form.hours.data:
        try:
            hours = int(form.hours.data)
            expires_at = utcnow() + timedelta(hours=hours)
        except ValueError:
            pass
    block = Block(
        user_id=form.user_id.data or None,
        ip_address=form.ip_address.data or None,
        reason=form.reason.data,
        expires_at=expires_at,
        active=True,
    )
    db.session.add(block)
    db.session.commit()
    flash('Block created.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/blocks/<int:block_id>/deactivate', methods=['POST'])
def deactivate_block(block_id):
    _admin_required()
    block = Block.query.get_or_404(block_id)
    block.active = False
    db.session.commit()
    flash('Block deactivated.', 'success')
    return redirect(url_for('admin_panel'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
