# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, DateTimeField, FileField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """
    Form for new user registration.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Validate that the username is not already in use.
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """
        Validate that the email is not already in use.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProfileForm(FlaskForm):
    """
    Form for updating user profile.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    currency = SelectField('Preferred Currency', choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')], validators=[DataRequired()])
    submit = SubmitField('Update')

class ChangePasswordForm(FlaskForm):
    """
    Form for changing user password.
    """
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField(
        'Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class Enable2FAForm(FlaskForm):
    """
    Form for enabling two-factor authentication.
    """
    submit = SubmitField('Enable 2FA')

class Verify2FAForm(FlaskForm):
    """
    Form for verifying two-factor authentication token.
    """
    token = StringField('2FA Token', validators=[DataRequired()])
    submit = SubmitField('Verify')

class RecurringTransactionForm(FlaskForm):
    """
    Form for managing recurring transactions.
    """
    amount = FloatField('Amount', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    interval = SelectField('Interval', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], validators=[DataRequired()])
    next_date = DateTimeField('Next Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Add Recurring Transaction')

class SearchForm(FlaskForm):
    """
    Form for advanced search and filtering of transactions.
    """
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    category = StringField('Category')
    submit = SubmitField('Search')

class InvestmentForm(FlaskForm):
    """
    Form for managing investments.
    """
    name = StringField('Investment Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Investment')

class TransactionForm(FlaskForm):
    """
    Form for uploading transaction receipt.
    """
    receipt = FileField('Receipt', validators=[DataRequired()])
    submit = SubmitField('Upload Receipt')
