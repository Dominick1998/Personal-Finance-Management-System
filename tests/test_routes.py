# tests/test_routes.py

import unittest
from app import app, db
from app.models import User

class RoutesTestCase(unittest.TestCase):
    """
    Test case for the application's routes.
    """

    def setUp(self):
        """
        Set up a temporary database for testing.
        This method is called before each test.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """
        Clean up the database after each test.
        This method is called after each test.
        """
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        """
        Test the home page route.
        Ensure it redirects to the login page if not authenticated.
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_login_page(self):
        """
        Test the login page route.
        Ensure the login page loads correctly.
        """
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_register_page(self):
        """
        Test the registration page route.
        Ensure the registration page loads correctly.
        """
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_successful_login(self):
        """
        Test the login process with valid credentials.
        """
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        # Attempt to log in with the test user's credentials
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_unsuccessful_login(self):
        """
        Test the login process with invalid credentials.
        """
        # Attempt to log in with incorrect credentials
        response = self.app.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_successful_registration(self):
        """
        Test the registration process with valid data.
        """
        # Attempt to register a new user
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'password2': 'newpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)

    def test_unsuccessful_registration(self):
        """
        Test the registration process with invalid data.
        """
        # Attempt to register with mismatched passwords
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'password2': 'wrongpassword'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be equal to password.', response.data)

if __name__ == '__main__':
    unittest.main()