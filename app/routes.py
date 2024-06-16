# app/routes.py

from flask import render_template, flash, redirect, url_for, request, abort, session, send_from_directory, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm, Enable2FAForm, Verify2FAForm, RecurringTransactionForm, SearchForm, InvestmentForm, TransactionForm, BackupForm, RestoreForm
from app.models import User, Transaction, RecurringTransaction, ActivityLog, Investment
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from functools import wraps
import pyotp
import os
import zipfile
import json

def admin_required(f):
    """
    Decorator to restrict access to admin users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
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

@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Home page route.
    """
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
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
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

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
def uploaded_file(filename):
    """
    Serve uploaded receipt files.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/backup', methods=['GET', 'POST'])
@login_required
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
