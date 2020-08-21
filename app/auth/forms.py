from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    ''' Prototype for Generating Login form with all the textfields and lables '''
    uName = StringField(_l('Username \ Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    rememberMe = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    ''' Prototype for Generating New  Registartion Form with all the textfields and lables '''
    uName = StringField(_l('User Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(),Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'), validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField(_l('Sign Up'))

    def validate_uName(self,uName):
        ''' Checks if the username is alreasy in use 
            this fucntion is called internally anything with a "validate_<field_name>" will be called 
            like other validators internally'''
        user = User.query.filter_by(username = uName.data).first()
        if user is not None:
            raise ValidationError(_('Please Use a different Username'))
    
    def validate_email(self, email):
        ''' Checks if the email is alreasy in use 
            this fucntion is called internally anything with a "validate_<field_name>" will be called 
            like other validators internally'''
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError(_('Please Use a different Email address'))


class ResetPasswordRequestForm(FlaskForm):
    '''  Form class used for Submiting request for resetting password  '''
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    '''  Form class used for Submiting the resetting of password  '''
    password1 = PasswordField(_l('Password'),validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'),validators=[DataRequired(),EqualTo('password1')])
    submit = SubmitField(_l('Reset Password'))

