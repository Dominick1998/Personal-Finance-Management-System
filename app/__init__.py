# app/__init__.py

# This file marks the 'app' directory as a Python package.
# It contains package-level initialization code, such as:
# - Setting up the application instance
# - Registering blueprints
# - Configuring extensions
# - Importing and defining package-level variables or functions

'''
The presence of this file allows the import from the 'app' package 
in other parts of your project, e.g., 'from app import some_module'.
'''

#start of code
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_oauthlib.client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_principal import Principal, Permission, RoleNeed
from flask_mail import Mail
from flask_apscheduler import APScheduler
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_swagger_ui import get_swaggerui_blueprint  # For API documentation
from flask_socketio import SocketIO  # For real-time communication
from flask_graphql import GraphQLView  # For GraphQL support
from flask_session import Session  # For server-side session management
from flask_cors import CORS  # For Cross-Origin Resource Sharing
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Enable server-side session management
Session(app)

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
    request_token_params={'scope': 'email'},
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
    request_token_params={'scope': 'email'},
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

# Configure image uploads
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Swagger configuration for API documentation
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Personal Finance Management System"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Initialize SocketIO
socketio = SocketIO(app)

# Register GraphQL view
from app.graphql_schema import schema
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

from app import routes, models, socketio_events

@login.user_loader
def load_user(id):
    """
    Load user by ID for Flask-Login.
    """
    return User.query.get(int(id))

# Session timeout configuration
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

# end