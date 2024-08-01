import pytest
from app import db
from app.models import User, Transaction, Investment

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
