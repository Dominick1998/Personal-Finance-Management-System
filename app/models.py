# app/models.py

from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64

# Generate a key for encryption (store this securely)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

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
    dashboard_config = db.Column(db.Text, default='{}')  # JSON config for dashboard widgets

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
    description = db.Column(db.String(256), nullable=False)  # Description for categorization
    receipt = db.Column(db.String(128))  # Path to receipt image
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    encrypted_data = db.Column(db.Text)  # Encrypted data column

    def __repr__(self):
        return f'<Transaction {self.amount} {self.category}>'

    def serialize(self):
        """
        Serialize transaction for backup.
        """
        return {
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'description': self.description,
            'receipt': self.receipt,
            'user_id': self.user_id
        }

    def encrypt(self):
        """
        Encrypt sensitive data.
        """
        data = f"{self.amount}|{self.category}|{self.date}|{self.description}|{self.receipt}"
        self.encrypted_data = cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self):
        """
        Decrypt sensitive data.
        """
        decrypted_data = cipher_suite.decrypt(self.encrypted_data.encode()).decode()
        amount, category, date, description, receipt = decrypted_data.split('|')
        self.amount = float(amount)
        self.category = category
        self.date = datetime.fromisoformat(date)
        self.description = description
        self.receipt = receipt

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

    def serialize(self):
        """
        Serialize recurring transaction for backup.
        """
        return {
            'amount': self.amount,
            'category': self.category,
            'interval': self.interval,
            'next_date': self.next_date.isoformat(),
            'user_id': self.user_id
        }

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

class Investment(db.Model):
    """
    Investment model for tracking user investments.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Investment {self.name} {self.amount}>'

    def serialize(self):
        """
        Serialize investment for backup.
        """
        return {
            'name': self.name,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'user_id': self.user_id
        }
