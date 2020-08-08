from flask_wtf import FlaskForm

from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    uName = StringField('User Name',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Sign In')