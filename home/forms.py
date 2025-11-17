from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from home.db_models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username has been taken, choose another.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email has been taken, choose another.')
            
class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username has been taken, choose another.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email has been taken, choose another.')
    
class UpdateSavingsForm(FlaskForm):
    savings = FloatField('Savings Balance ($)', validators=[DataRequired(), NumberRange(min=0, message='Savings cannot be negative')])
    submit = SubmitField('Update Savings')

class AdjustSavingsForm(FlaskForm):
    amount = FloatField('Amount ($)', validators=[DataRequired()])
    operation = SelectField('Operation', choices=[
        ('add', 'Add to savings'),
        ('subtract', 'Subtract from savings')
    ], validators=[DataRequired()])
    description = StringField('Description (Optional)', validators=[Optional()])
    submit = SubmitField('Adjust Savings')

class GoalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    url = StringField('URL (Optional)', validators=[Optional()])
    target_amount = FloatField('Target Amount ($)', validators=[DataRequired()])
    deadline = DateField('Deadline (Optional)', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('savings', 'Savings'),
        ('investment', 'Investment'),
        ('emergency', 'Emergency Fund'),
        ('vacation', 'Vacation'),
        ('education', 'Education'),
        ('home', 'Home'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other')
    ], validators=[Optional()])
    submit = SubmitField('Create Goal')

    def validate_target_amount(self, target_amount):
        if target_amount.data <= 0:
            raise ValidationError('Target amount must be greater than 0.')
        if target_amount.data > 1000000:  # Optional: add upper limit
            raise ValidationError('Target amount cannot exceed $1,000,000.')

class UpdateGoalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    url = StringField('URL (Optional)', validators=[Optional()])
    target_amount = FloatField('Target Amount ($)', validators=[DataRequired()])
    deadline = DateField('Deadline (Optional)', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('savings', 'Savings'),
        ('investment', 'Investment'),
        ('emergency', 'Emergency Fund'),
        ('vacation', 'Vacation'),
        ('education', 'Education'),
        ('home', 'Home'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other')
    ], validators=[Optional()])
    submit = SubmitField('Update Goal')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class UserPreferencesForm(FlaskForm):
    theme = SelectField('Theme', choices=[
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode')
    ], validators=[DataRequired()])
    notifications = BooleanField('Enable Notifications')
    submit = SubmitField('Save Preferences')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    currency = SelectField('Currency', choices=[
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
        ('CAD', 'CAD (C$)'),
        ('AUD', 'AUD (A$)')
    ], validators=[DataRequired()])
    is_open = BooleanField('Open Group to Public', default=True)
    submit = SubmitField('Create Group')

class JoinGroupForm(FlaskForm):
    group_id = IntegerField('Group ID', validators=[DataRequired()])
    message = TextAreaField('Message (Optional)', validators=[Optional()])
    submit = SubmitField('Join Group')

class GroupGoalForm(FlaskForm):
    title = StringField('Goal Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    target_amount = FloatField('Target Amount', validators=[
        DataRequired(), 
        NumberRange(min=0.01, message='Target amount must be greater than 0')
    ])
    deadline = DateField('Deadline (Optional)', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('savings', 'Savings'),
        ('investment', 'Investment'),
        ('emergency', 'Emergency Fund'),
        ('vacation', 'Vacation'),
        ('education', 'Education'),
        ('home', 'Home'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other')
    ], validators=[Optional()])
    submit = SubmitField('Propose Goal')

class GroupTransactionForm(FlaskForm):
    amount = FloatField('Amount', validators=[
        DataRequired(), 
        NumberRange(min=0.01, message='Amount must be greater than 0')
    ])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit Transaction')

class GroupPreferencesForm(FlaskForm):
    default_graph_type = SelectField('Default Graph Type', choices=[
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart')
    ], validators=[DataRequired()])
    currency = SelectField('Currency', choices=[
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
        ('CAD', 'CAD (C$)'),
        ('AUD', 'AUD (A$)')
    ], validators=[DataRequired()])
    is_open = BooleanField('Open Group (Anyone can request to join)')
    submit = SubmitField('Save Preferences')