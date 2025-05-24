# app/routes.py | route definitions

"""
This file contains the route definitions for the Personal Finance Management System.
It handles HTTP requests and defines the behavior for each route.

Routes:
    - Home Page: Displays the main dashboard for the user.
    - Login: Handles user login with support for rate limiting and OAuth2 login via Google and Facebook.
    - Logout: Logs the user out of the application.
    - Register: Handles user registration and sends a confirmation email.
    - Email Confirmation: Confirms the user's email address.
    - Profile: Allows the user to view and update their profile.
    - Change Password: Allows the user to change their password.
    - Admin Dashboard: Displays the admin dashboard for managing users and transactions.
    - Financial Analytics: Provides data for financial trend analysis.
    - Enable 2FA: Enables two-factor authentication for the user.
    - Verify 2FA: Verifies the user's two-factor authentication code.
    - Recurring Transactions: Manages the user's recurring transactions.
    - Advanced Search: Allows the user to search and filter transactions.
    - Investments: Manages the user's investments.
    - Upload Receipt: Allows the user to upload a receipt for a transaction.
    - Serve Uploaded Files: Serves uploaded receipt files.
    - Backup: Backs up the user's data.
    - Restore: Restores the user's data from a backup.
    - Dashboard Configuration: Updates the user's dashboard configuration.
    - Categorize Transaction: Categorizes a transaction using a machine learning model.
    - Plaid Link: Links the user's bank account with Plaid and imports transactions.
    - Send Notification: Sends a notification to users (admin only).
    - Notification Preferences: Manages the user's notification preferences.
    - Export Data: Exports the user's data in the specified format.
    - Delete Account: Deletes the user's account.
    - Share Goal: Shares the user's financial goal on social media.
    - Convert Currency: Converts an amount from one currency to another.
    - Upload Profile Picture: Allows the user to upload a profile picture.
    - Voice Commands: Handles voice commands for the application.
    - Mobile API: Provides an API endpoint for integrating with the mobile app.
    - Fraud Detection: Detects potentially fraudulent transactions using AI.

Utilities:
    - admin_required: Decorator to restrict access to admin users.
    - user_required: Decorator to restrict access to regular users.
    - log_activity: Logs user activity.
    - generate_confirmation_token: Generates an email confirmation token.
    - confirm_token: Confirms the token and returns the email.
    - send_email: Sends an email.
    - check_session_timeout: Checks if the session has timed out.

Dependencies:
    - Flask: Web framework for creating the application backend.
    - SQLAlchemy: ORM for managing database interactions.
    - Flask-Login: User session management for login functionality.
    - Flask-OAuthlib: OAuth2 integration for Google and Facebook login.
    - Flask-Limiter: Rate limiting to prevent brute force attacks.
    - Flask-Mail: Sending emails.
    - PyOTP: Two-factor authentication (2FA).
    - Joblib: Loading machine learning models.
    - Requests: Handling HTTP requests (used by Plaid API).
    - Werkzeug: WSGI utility library.
    - JSON: Handling JSON data.
    - Itsdangerous: Generating and confirming tokens.
    - OS: Handling file paths and operations.
    - DateTime: Handling date and time operations.
    - Functools: Higher-order functions and operations on callable objects.
    - Flask-Uploads: Handling file uploads.
    - Flask-Swagger-UI: API documentation using Swagger.
"""

from flask import render_template, flash, redirect, url_for, request, abort, session, jsonify, send_file
from app import app, db, google, facebook, limiter, admin_permission, user_permission, mail, scheduler, photos, socketio
from app.forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm, Enable2FAForm, Verify2FAForm, RecurringTransactionForm, SearchForm, InvestmentForm, TransactionForm, BackupForm, RestoreForm, CategorizeTransactionForm, PlaidLinkForm, NotificationForm, NotificationPreferencesForm, EmailVerificationForm, DeleteAccountForm, SocialShareForm, UploadProfilePictureForm, FraudDetectionForm
from app.models import User, Transaction, RecurringTransaction, ActivityLog, Investment, Role, UserNotification, FraudDetection
from app.plaid_utils import get_accounts, get_transactions
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from functools import wraps
import pyotp
import os
import json
import joblib
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from datetime import datetime, timedelta
import requests

def admin_required(f):
    """
    Decorator to restrict access to admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not admin_permission.can():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """
    Decorator to restrict access to regular users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not user_permission.can():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action):
    """
    Log user activity.
    """
    activity = ActivityLog(user_id=user_id, action=action)
    db.session.add(activity)
    db.session.commit()

def generate_confirmation_token(email):
    """
    Generate an email confirmation token.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    """
    Confirm the token and return the email.
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_email(to, subject, template):
    """
    Send an email.
    """
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def check_session_timeout():
    """
    Check if the session has timed out and log out the user if necessary.
    """
    if 'last_activity' in session:
        now = datetime.now()
        last_activity = session['last_activity']
        if (now - last_activity).seconds > app.permanent_session_lifetime.seconds:
            session.pop('user_id', None)
            flash('Session timed out. Please log in again.', 'warning')
            return redirect(url_for('login'))
    session['last_activity'] = datetime.now()

@app.before_request
def before_request():
    """
    Ensure session timeout is checked before each request.
    """
    if current_user.is_authenticated:
        check_session_timeout()

@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Home page route.
    """
    # Load user dashboard configuration
    dashboard_config = json.loads(current_user.dashboard_config)
    return render_template('index.html', title='Home', dashboard_config=dashboard_config)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limiting for login attempts
def login():
    """
    Login page route.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('resend_verification'))
        if user.two_factor_enabled:
            session['2fa_user_id'] = user.id
            return redirect(url_for('verify_2fa'))
        login_user(user, remember=form.remember_me.data)
        log_activity(user.id, 'User logged in')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/login/google')
def login_google():
    """
    Google login route.
    """
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/google/authorized')
def authorized():
    """
    Google login callback route.
    """
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('login'))

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    # Implement your logic to handle user info and login/register the user
    # Example: Check if user exists, if not, create a new user
    user = User.query.filter_by(email=user_info.data['email']).first()
    if user is None:
        user = User(username=user_info.data['email'], email=user_info.data['email'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    log_activity(user.id, 'User logged in with Google')
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    """
    Retrieve Google OAuth token.
    """
    return session.get('google_token')

@app.route('/login/facebook')
def login_facebook():
    """
    Facebook login route.
    """
    return facebook.authorize(callback=url_for('facebook_authorized', _external=True))

@app.route('/login/facebook/authorized')
def facebook_authorized():
    """
    Facebook login callback route.
    """
    response = facebook.authorized_response()
    if response is None or response.get('access_token') is None:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('login'))

    session['facebook_token'] = (response['access_token'], '')
    user_info = facebook.get('me?fields=id,email')
    # Implement your logic to handle user info and login/register the user
    # Example: Check if user exists, if not, create a new user
    user = User.query.filter_by(email=user_info.data['email']).first()
    if user is None:
        user = User(username=user_info.data['email'], email=user_info.data['email'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    log_activity(user.id, 'User logged in with Facebook')
    return redirect(url_for('index'))

@facebook.tokengetter
def get_facebook_oauth_token():
    """
    Retrieve Facebook OAuth token.
    """
    return session.get('facebook_token')

@app.route('/logout')
def logout():
    """
    Logout route.
    """
    log_activity(current_user.id, 'User logged out')
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page route.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/confirm/<token>')
def confirm_email(token):
    """
    Confirm email route.
    """
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.email_verified:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.email_verified = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

@app.route('/resend')
def resend_verification():
    """
    Resend email verification route.
    """
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile page route.
    """
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.currency = form.currency.data  # Save selected currency
        db.session.commit()
        log_activity(current_user.id, 'User updated profile')
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.currency.data = current_user.currency  # Pre-select user's currency
    return render_template('profile.html', title='Profile', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password page route.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_activity(current_user.id, 'User changed password')
            flash('Your password has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Old password is incorrect.', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """
    Admin dashboard route.
    """
    return render_template('admin_dashboard.html', title='Admin Dashboard')

@app.route('/analytics')
@login_required
@user_required
def analytics():
    """
    Financial analytics page route.
    Provides data for financial trend analysis.
    """
    # Example data, replace with your query to fetch actual data
    labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
    data = [100, 200, 150, 300, 250, 400, 350]
    return render_template('analytics.html', labels=labels, data=data)

@app.route('/enable_2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    """
    Enable two-factor authentication route.
    """
    form = Enable2FAForm()
    if form.validate_on_submit():
        current_user.two_factor_enabled = True
        current_user.two_factor_secret = pyotp.random_base32()
        db.session.commit()
        flash('Two-factor authentication has been enabled!', 'success')
        return redirect(url_for('profile'))
    return render_template('enable_2fa.html', title='Enable 2FA', form=form, secret=pyotp.random_base32())

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    """
    Verify two-factor authentication route.
    """
    if '2fa_user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['2fa_user_id'])
    form = Verify2FAForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(form.token.data):
            login_user(user)
            session.pop('2fa_user_id')
            log_activity(user.id, 'User logged in with 2FA')
            return redirect(url_for('index'))
        else:
            flash('Invalid 2FA token.', 'danger')
            return redirect(url_for('verify_2fa'))
    return render_template('verify_2fa.html', title='Verify 2FA', form=form)

@app.route('/recurring_transactions', methods=['GET', 'POST'])
@login_required
@user_required
def recurring_transactions():
    """
    Manage recurring transactions route.
    """
    form = RecurringTransactionForm()
    if form.validate_on_submit():
        transaction = RecurringTransaction(
            amount=form.amount.data,
            category=form.category.data,
            interval=form.interval.data,
            next_date=form.next_date.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        log_activity(current_user.id, 'Added recurring transaction')
        flash('Recurring transaction has been added!', 'success')
        return redirect(url_for('recurring_transactions'))
    transactions = RecurringTransaction.query.filter_by(user_id=current_user.id).all()
    return render_template('recurring_transactions.html', title='Recurring Transactions', form=form, transactions=transactions)

@app.route('/search', methods=['GET', 'POST'])
@login_required
@user_required
def search():
    """
    Advanced search and filtering route.
    """
    form = SearchForm()
    transactions = []
    if form.validate_on_submit():
        query = Transaction.query.filter_by(user_id=current_user.id)
        if form.start_date.data:
            query = query.filter(Transaction.date >= form.start_date.data)
        if form.end_date.data:
            query = query.filter(Transaction.date <= form.end_date.data)
        if form.category.data:
            query = query.filter_by(category=form.category.data)
        transactions = query.all()
        log_activity(current_user.id, 'Performed search')
    return render_template('search.html', title='Search', form=form, transactions=transactions)

@app.route('/investments', methods=['GET', 'POST'])
@login_required
@user_required
def investments():
    """
    Manage investments route.
    """
    form = InvestmentForm()
    if form.validate_on_submit():
        investment = Investment(
            name=form.name.data,
            amount=form.amount.data,
            user_id=current_user.id
        )
        db.session.add(investment)
        db.session.commit()
        log_activity(current_user.id, 'Added investment')
        flash('Investment has been added!', 'success')
        return redirect(url_for('investments'))
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    return render_template('investments.html', title='Investments', form=form, investments=investments)

@app.route('/upload_receipt/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@user_required
def upload_receipt(transaction_id):
    """
    Upload receipt for a transaction route.
    """
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction.query.get(transaction_id)
        if transaction.user_id != current_user.id:
            abort(403)
        file = form.receipt.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        transaction.receipt = filename
        db.session.commit()
        log_activity(current_user.id, f'Uploaded receipt for transaction {transaction_id}')
        flash('Receipt has been uploaded!', 'success')
        return redirect(url_for('index'))
    return render_template('upload_receipt.html', title='Upload Receipt', form=form)

@app.route('/uploads/<filename>')
@login_required
@user_required
def uploaded_file(filename):
    """
    Serve uploaded receipt files.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/backup', methods=['GET', 'POST'])
@login_required
@user_required
def backup():
    """
    Backup user data route.
    """
    form = BackupForm()
    if form.validate_on_submit():
        user_data = {
            'transactions': [t.serialize() for t in Transaction.query.filter_by(user_id=current_user.id).all()],
            'investments': [i.serialize() for i in Investment.query.filter_by(user_id=current_user.id).all()],
            'recurring_transactions': [rt.serialize() for rt in RecurringTransaction.query.filter_by(user_id=current_user.id).all()]
        }
        backup_path = os.path.join(app.config['BACKUP_FOLDER'], f'backup_{current_user.id}.json')
        with open(backup_path, 'w') as backup_file:
            json.dump(user_data, backup_file)
        flash('Your data has been backed up successfully!', 'success')
        return send_from_directory(app.config['BACKUP_FOLDER'], f'backup_{current_user.id}.json', as_attachment=True)
    return render_template('backup.html', title='Backup Data', form=form)

@app.route('/restore', methods=['GET', 'POST'])
@login_required
@user_required
def restore():
    """
    Restore user data route.
    """
    form = RestoreForm()
    if form.validate_on_submit():
        file = form.backup_file.data
        if file:
            data = json.load(file)
            for t_data in data.get('transactions', []):
                transaction = Transaction(**t_data)
                db.session.add(transaction)
            for i_data in data.get('investments', []):
                investment = Investment(**i_data)
                db.session.add(investment)
            for rt_data in data.get('recurring_transactions', []):
                recurring_transaction = RecurringTransaction(**rt_data)
                db.session.add(recurring_transaction)
            db.session.commit()
            flash('Your data has been restored successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('restore.html', title='Restore Data', form=form)

@app.route('/dashboard_config', methods=['POST'])
@login_required
@user_required
def dashboard_config():
    """
    Update user dashboard configuration route.
    """
    data = request.get_json()
    current_user.dashboard_config = json.dumps(data)
    db.session.commit()
    log_activity(current_user.id, 'Updated dashboard configuration')
    return jsonify({'status': 'success'})

@app.route('/categorize_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@user_required
def categorize_transaction(transaction_id):
    """
    Categorize transaction using machine learning model route.
    """
    transaction = Transaction.query.get(transaction_id)
    if transaction.user_id != current_user.id:
        abort(403)
    form = CategorizeTransactionForm()
    if form.validate_on_submit():
        model = joblib.load('model/transaction_categorizer.pkl')
        category = model.predict([form.description.data])
        transaction.category = category[0]
        db.session.commit()
        log_activity(current_user.id, f'Categorized transaction {transaction_id}')
        flash('Transaction has been categorized!', 'success')
        return redirect(url_for('index'))
    return render_template('categorize_transaction.html', title='Categorize Transaction', form=form, transaction=transaction)

@app.route('/plaid_link', methods=['GET', 'POST'])
@login_required
@user_required
def plaid_link():
    """
    Link bank account with Plaid route.
    """
    form = PlaidLinkForm()
    if form.validate_on_submit():
        access_token = 'YOUR_PLAID_ACCESS_TOKEN'
        accounts = get_accounts(access_token)
        transactions = get_transactions(access_token, start_date='2023-01-01', end_date='2023-12-31')
        for txn in transactions:
            new_transaction = Transaction(
                amount=txn['amount'],
                category=txn['category'][0],
                date=txn['date'],
                description=txn['name'],
                user_id=current_user.id
            )
            db.session.add(new_transaction)
        db.session.commit()
        log_activity(current_user.id, 'Linked bank account with Plaid')
        flash('Bank account linked and transactions imported!', 'success')
        return redirect(url_for('index'))
    return render_template('plaid_link.html', title='Link Bank Account', form=form)

@app.route('/send_notification', methods=['GET', 'POST'])
@login_required
@admin_required
def send_notification():
    """
    Send notification to users.
    """
    form = NotificationForm()
    if form.validate_on_submit():
        # Logic to send notification (e.g., email, SMS)
        flash('Notification sent successfully!', 'success')
        return redirect(url_for('send_notification'))
    return render_template('send_notification.html', title='Send Notification', form=form)

@app.route('/notification_preferences', methods=['GET', 'POST'])
@login_required
@user_required
def notification_preferences():
    """
    Manage user notification preferences route.
    """
    form = NotificationPreferencesForm()
    if form.validate_on_submit():
        current_user.notification_preferences = json.dumps(form.data)
        db.session.commit()
        log_activity(current_user.id, 'Updated notification preferences')
        flash('Notification preferences updated!', 'success')
        return redirect(url_for('notification_preferences'))
    elif request.method == 'GET':
        form.data = json.loads(current_user.notification_preferences or '{}')
    return render_template('notification_preferences.html', title='Notification Preferences', form=form)

@app.route('/export_data/<format>')
@login_required
@user_required
def export_data(format):
    """
    Export user data in specified format (e.g., JSON, PDF).
    """
    user_data = {
        'transactions': [t.serialize() for t in Transaction.query.filter_by(user_id=current_user.id).all()],
        'investments': [i.serialize() for i in Investment.query.filter_by(user_id=current_user.id).all()],
        'recurring_transactions': [rt.serialize() for rt in RecurringTransaction.query.filter_by(user_id=current_user.id).all()]
    }

    if format == 'json':
        export_path = os.path.join(app.config['EXPORT_FOLDER'], f'export_{current_user.id}.json')
        with open(export_path, 'w') as export_file:
            json.dump(user_data, export_file)
        return send_file(export_path, as_attachment=True)

    elif format == 'pdf':
        # Logic to export data as PDF
        pass

    flash('Export format not supported.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
@user_required
def delete_account():
    """
    Delete user account route.
    """
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user = current_user
        log_activity(user.id, 'User deleted account')
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('login'))
    return render_template('delete_account.html', title='Delete Account', form=form)

@app.route('/share_goal', methods=['GET', 'POST'])
@login_required
@user_required
def share_goal():
    """
    Share financial goal on social media route.
    """
    form = SocialShareForm()
    if form.validate_on_submit():
        # Logic to share goal on social media (e.g., Twitter, Facebook)
        flash('Your goal has been shared!', 'success')
        return redirect(url_for('index'))
    return render_template('share_goal.html', title='Share Goal', form=form)

@app.route('/convert_currency', methods=['POST'])
@login_required
@user_required
def convert_currency():
    """
    Convert currency route.
    """
    amount = request.form.get('amount')
    from_currency = request.form.get('from_currency')
    to_currency = request.form.get('to_currency')

    # Example: Real-time currency conversion using an API
    response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_currency}')
    data = response.json()
    converted_amount = float(amount) * data['rates'][to_currency]

    return jsonify({'converted_amount': converted_amount})

@app.route('/upload_profile_picture', methods=['GET', 'POST'])
@login_required
@user_required
def upload_profile_picture():
    """
    Upload profile picture route.
    """
    form = UploadProfilePictureForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        current_user.profile_picture = filename
        db.session.commit()
        log_activity(current_user.id, 'Uploaded profile picture')
        flash('Profile picture has been uploaded!', 'success')
        return redirect(url_for('profile'))
    return render_template('upload_profile_picture.html', title='Upload Profile Picture', form=form)

@app.route('/api/voice_commands', methods=['POST'])
@login_required
@user_required
def voice_commands():
    """
    Handle voice commands for the application.
    """
    command = request.json.get('command')
    # Logic to process the voice command and return a response
    response = process_voice_command(command)
    return jsonify({'response': response})

@app.route('/api/mobile', methods=['POST'])
@login_required
@user_required
def mobile_api():
    """
    Mobile API endpoint for integrating with the mobile app.
    """
    data = request.json
    # Logic to handle data from the mobile app
    process_mobile_data(data)
    return jsonify({'status': 'success'})

@app.route('/fraud_detection', methods=['GET', 'POST'])
@login_required
@admin_required
def fraud_detection():
    """
    Fraud detection route.
    """
    form = FraudDetectionForm()
    if form.validate_on_submit():
        # Logic to detect fraudulent transactions using AI
        flash('Fraud detection executed successfully!', 'success')
        return redirect(url_for('fraud_detection'))
    return render_template('fraud_detection.html', title='Fraud Detection', form=form)
