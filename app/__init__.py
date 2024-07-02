# app/__init__.py

# This file marks the 'app' directory as a Python package.
# It may also contain package-level initialization code, such as:
# - Setting up the application instance
# - Registering blueprints

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_oauthlib.client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_principal import Principal, Permission, RoleNeed
from flask_mail import Mail
from flask_apscheduler import APScheduler
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# Initialize OAuth for Google and Facebook Login
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_CLIENT_ID'],
    consumer_secret=app.config['GOOGLE_CLIENT_SECRET'],
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=app.config['FACEBOOK_CLIENT_ID'],
    consumer_secret=app.config['FACEBOOK_CLIENT_SECRET'],
    request_token_params={
        'scope': 'email',
    },
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Flask-Principal for RBAC
principals = Principal(app)

# Define permissions for different roles
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))

# Initialize Flask-Mail
mail = Mail(app)

# Initialize APScheduler for scheduled tasks
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import routes, models

@login.user_loader
def load_user(id):
    """
    Load user by ID for Flask-Login.
    """
    return User.query.get(int(id))
