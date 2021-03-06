from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User
from flask import request


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


class SearchForm(FlaskForm):
    '''  Form class used for Searching functionality  '''
    query = StringField(_l('Search'), validators=[DataRequired()])
    def __init__(self,*args,**kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    '''  Form class used for message functionality  '''
    message = TextAreaField(_l('Message'),validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class CommentForm(FlaskForm):
    '''  Form class used for Comment functionality  '''
    body = TextAreaField(_l('Comment'),validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

