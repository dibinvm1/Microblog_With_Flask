from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo,Length
from app.models import User

class LoginForm(FlaskForm):
    ''' Prototype for Generating Login form with all the textfields and lables '''
    uName = StringField(_l('User Name'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    rememberMe = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegristrationForm(FlaskForm):
    ''' Prototype for Generating New  Registartion Form with all the textfields and lables '''
    uName = StringField(_l('User Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(),Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm PassWord'), validators=[DataRequired(),EqualTo('password')])
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


class EditProfileForm(FlaskForm):
    ''' Form class for editing profile cnotains username,aboutMe editing functinality '''
    uName = StringField(_l('User Name'), validators=[DataRequired()])
    aboutMe = TextAreaField(_l('About Me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self,oroginal_username,*args,**kwargs):
        ''' re-init of the Form class for adding the original username '''
        super(EditProfileForm,self).__init__(*args,**kwargs)
        self.oroginal_username = oroginal_username

    def validate_uName(self,uName):
        ''' Checks if the username is alreasy in use excluding the original username
            this fucntion is called internally anything with a "validate_<field_name>" will be called 
            like other validators internally'''
        if uName.data != self.oroginal_username:
            user = User.query.filter_by(username = self.uName.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username'))

class EmptyForm(FlaskForm):
    ''' Empty Form class used for Follow and Unfollow functionality
     contains a single button '''
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    '''  Form class used for Posting message functionality  '''
    post = TextAreaField(_l('Say Something'),validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    '''  Form class used for Submiting request for resetting password  '''
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    '''  Form class used for Submiting the resetting of password  '''
    password1 = PasswordField(_l('Password'),validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'),validators=[DataRequired(),EqualTo('password1')])
    submit = SubmitField(_l('Reset Password'))

