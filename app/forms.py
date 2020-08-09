from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    uName = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegristrationForm(FlaskForm):
    uName = StringField('User Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm PassWord', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_uName(self,uName):
        user = User.query.filter_by(username = uName.data).first()
        if user is not None:
            raise ValidationError('Please Use a different Username')
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('Please Use a different Email address')
