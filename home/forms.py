from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from home.db_models import User
from flask_wtf.file import FileField, FileAllowed
#from flask_login import current_user

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
    
    '''
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
    '''
    
class GoalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
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
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Goal')