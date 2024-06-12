# app/models.py

from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """
    User model for storing user details and roles.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='user')  # User role for access control
    currency = db.Column(db.String(3), default='USD')  # Preferred currency
    two_factor_enabled = db.Column(db.Boolean, default=False)  # 2FA enabled
    two_factor_secret = db.Column(db.String(32))  # 2FA secret key

    def set_password(self, password):
        """
        Set password for the user.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password matches the stored password hash.
        """
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    """
    Load user by ID for Flask-Login.
    """
    return User.query.get(int(id))

class Transaction(db.Model):
    """
    Transaction model for storing income and expense details.
    """
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Transaction {self.amount} {self.category}>'

class RecurringTransaction(db.Model):
    """
    RecurringTransaction model for storing recurring income and expense details.
    """
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    interval = db.Column(db.String(32), nullable=False)  # e.g., 'daily', 'weekly', 'monthly'
    next_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<RecurringTransaction {self.amount} {self.category} {self.interval}>'

class ActivityLog(db.Model):
    """
    ActivityLog model for storing user activity logs.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityLog {self.user_id} {self.action} {self.timestamp}>'
