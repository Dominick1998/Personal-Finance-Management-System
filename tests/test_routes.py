# test routes
# pytest 

import pytest
from app import app, db
from app.models import User, Transaction, Investment
from io import BytesIO
import pyotp

@pytest.fixture
def client():
    """
    Set up the test client for Flask application.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    with app.app_context():
        db.drop_all()

@pytest.fixture
def init_database():
    """
    Initialize the database with a test user.
    """
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

def test_index(client, init_database):
    """
    Test the index route which should redirect to login if not authenticated.
    """
    response = client.get('/')
    assert response.status_code == 302  # Redirects to login

def test_login(client, init_database):
    """
    Test the login functionality.
    """
    response = client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_register(client):
    """
    Test the registration functionality.
    """
    response = client.post('/register', data=dict(
        username='newuser',
        email='newuser@example.com',
        password='password',
        password2='password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'A confirmation email has been sent' in response.data

def test_profile(client, init_database):
    """
    Test the profile update functionality.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/profile', data=dict(
        username='updateduser',
        email='updated@example.com'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Your profile has been updated!' in response.data

def test_add_recurring_transaction(client, init_database):
    """
    Test adding a recurring transaction.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/recurring_transactions', data=dict(
        amount=100,
        category='Utilities',
        interval='Monthly',
        next_date='2024-07-01'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Recurring transaction has been added!' in response.data

def test_upload_receipt(client, init_database):
    """
    Test uploading a receipt for a transaction.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    transaction = Transaction(amount=100, description='Test Transaction', user_id=1)
    db.session.add(transaction)
    db.session.commit()
    data = {
        'receipt': (BytesIO(b'my file contents'), 'receipt.txt')
    }
    response = client.post(f'/upload_receipt/{transaction.id}', content_type='multipart/form-data', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Receipt has been uploaded!' in response.data

def test_backup_and_restore(client, init_database):
    """
    Test backing up and restoring user data.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/backup', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your data has been backed up successfully!' in response.data
    
    # Simulate file upload for restore
    backup_data = {
        'backup_file': (BytesIO(response.data), 'backup.json')
    }
    response = client.post('/restore', content_type='multipart/form-data', data=backup_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your data has been restored successfully!' in response.data

def test_enable_2fa(client, init_database):
    """
    Test enabling two-factor authentication (2FA).
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/enable_2fa', follow_redirects=True)
    assert response.status_code == 200
    assert b'Two-factor authentication has been enabled!' in response.data

def test_verify_2fa(client, init_database):
    """
    Test verifying two-factor authentication (2FA).
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    client.post('/enable_2fa', follow_redirects=True)
    user = User.query.filter_by(username='testuser').first()
    totp = pyotp.TOTP(user.two_factor_secret)
    token = totp.now()
    response = client.post('/verify_2fa', data=dict(token=token), follow_redirects=True)
    assert response.status_code == 200
    assert b'User logged in with 2FA' in response.data

def test_categorize_transaction(client, init_database):
    """
    Test categorizing a transaction using a machine learning model.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    transaction = Transaction(amount=100, description='Test Transaction', user_id=1)
    db.session.add(transaction)
    db.session.commit()
    response = client.post(f'/categorize_transaction/{transaction.id}', data=dict(
        description='Grocery shopping'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Transaction has been categorized!' in response.data

def test_notification_preferences(client, init_database):
    """
    Test updating notification preferences.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/notification_preferences', data=dict(
        email_notifications=True,
        sms_notifications=False
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Notification preferences updated!' in response.data

def test_delete_account(client, init_database):
    """
    Test deleting a user account.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/delete_account', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your account has been deleted.' in response.data

def test_export_data(client, init_database):
    """
    Test exporting user data.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.get('/export_data/json', follow_redirects=True)
    assert response.status_code == 200
    assert b'Content-Type: application/json' in response.headers['Content-Type']

def test_share_goal(client, init_database):
    """
    Test sharing a financial goal on social media.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/share_goal', data=dict(
        goal='Save $5000 for a vacation'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Your goal has been shared!' in response.data

def test_convert_currency(client, init_database):
    """
    Test currency conversion.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/convert_currency', data=dict(
        amount=100,
        from_currency='USD',
        to_currency='EUR'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'converted_amount' in response.json

def test_upload_profile_picture(client, init_database):
    """
    Test uploading a profile picture.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    data = {
        'photo': (BytesIO(b'my file contents'), 'profile.jpg')
    }
    response = client.post('/upload_profile_picture', content_type='multipart/form-data', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile picture has been uploaded!' in response.data

def test_voice_commands(client, init_database):
    """
    Test handling voice commands.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/api/voice_commands', json=dict(
        command='Show my budget'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'response' in response.json

def test_mobile_api(client, init_database):
    """
    Test the mobile API endpoint.
    """
    client.post('/login', data=dict(
        username='testuser',
        password='password'
    ), follow_redirects=True)
    response = client.post('/api/mobile', json=dict(
        data='Test data'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'status' in response.json
