# app/models.py

from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """
    User model for storing user details.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    currency = db.Column(db.String(3), default='USD')
    dashboard_config = db.Column(db.Text)
    notification_preferences = db.Column(db.Text)
    roles = db.relationship('Role', secondary='user_roles')

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
    description = db.Column(db.String(255))
    receipt = db.Column(db.String(255))
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
    interval = db.Column(db.String(64), nullable=False)
    next_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<RecurringTransaction {self.amount} {self.category} {self.interval}>'

class ActivityLog(db.Model):
    """
    ActivityLog model for logging user activities.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityLog {self.user_id} {self.action}>'

class Investment(db.Model):
    """
    Investment model for storing investment details.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Investment {self.name} {self.amount}>'

class Role(db.Model):
    """
    Role model for storing user roles.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class UserRoles(db.Model):
    """
    UserRoles model for associating users with roles.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

class UserNotification(db.Model):
    """
    UserNotification model for storing user notifications.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserNotification {self.user_id} {self.message}>'
