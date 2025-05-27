# app/forms.py
# forms for login/registration, etc.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, DateTimeField, FileField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1,
)

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

    def validate_password(self, password):
        """
        Validate that the password meets the strength requirements.
        """
        errors = policy.test(password.data)
        if errors:
            raise ValidationError('Password must be at least 8 characters long and include one uppercase letter, one number, and one special character.')

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

class BackupForm(FlaskForm):
    """
    Form for backing up user data.
    """
    submit = SubmitField('Backup Data')

class RestoreForm(FlaskForm):
    """
    Form for restoring user data.
    """
    backup_file = FileField('Backup File', validators=[DataRequired()])
    submit = SubmitField('Restore Data')

class CategorizeTransactionForm(FlaskForm):
    """
    Form for categorizing a transaction using a machine learning model.
    """
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Categorize Transaction')

class PlaidLinkForm(FlaskForm):
    """
    Form for linking bank account with Plaid.
    """
    public_token = StringField('Public Token', validators=[DataRequired()])
    submit = SubmitField('Link Account')

class NotificationForm(FlaskForm):
    """
    Form for sending notifications to users.
    """
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Notification')

class NotificationPreferencesForm(FlaskForm):
    """
    Form for managing user notification preferences.
    """
    preferences = SelectMultipleField('Notification Preferences', choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Preferences')

class EmailVerificationForm(FlaskForm):
    """
    Form for resending email verification.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Verification')

class DeleteAccountForm(FlaskForm):
    """
    Form for deleting user account.
    """
    submit = SubmitField('Delete Account')

class SocialShareForm(FlaskForm):
    """
    Form for sharing financial goals on social media.
    """
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Share')

class UploadProfilePictureForm(FlaskForm):
    """
    Form for uploading profile picture.
    """
    photo = FileField('Profile Picture', validators=[DataRequired()])
    submit = SubmitField('Upload')
