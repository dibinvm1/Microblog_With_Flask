from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo,Length
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


class EditProfileForm(FlaskForm):
    uName = StringField('User Name', validators=[DataRequired()])
    aboutMe = TextAreaField('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self,oroginal_username,*args,**kwargs):
        super(EditProfileForm,self).__init__(*args,**kwargs)
        self.oroginal_username = oroginal_username

    def validate_uName(self,uName):
        if uName.data != self.oroginal_username:
            user = User.query.filter_by(username = self.uName.data).first()
            if user is not None:
                raise ValidationError('Please use a different username')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say Something',validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Submit")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password1 = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password1')])
    submit = SubmitField('Reset Password')
