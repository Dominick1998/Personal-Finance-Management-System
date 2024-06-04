# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize Flask-Login for user session management
login = LoginManager(app)
login.login_view = 'login'  # Set the login view to 'login'

# Import routes and models
from app import routes, models
