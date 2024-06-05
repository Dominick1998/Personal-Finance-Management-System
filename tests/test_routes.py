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
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """
        Clean up the database after each test.
        """
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        """
        Test the home page route.
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_login_page(self):
        """
        Test the login page route.
        """
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_register_page(self):
        """
        Test the registration page route.
        """
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

if __name__ == '__main__':
    unittest.main()
