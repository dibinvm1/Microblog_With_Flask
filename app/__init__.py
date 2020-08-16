from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

app = Flask(__name__)                   #initializing the app
app.config.from_object(Config)          
db = SQLAlchemy(app)                    #initializing SQLalchemy
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'               
login.login_message = _l('Please login to Access this page')
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)

from app import routes , models, errors


''' Setting up a file logging system '''
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs') 
    ''' Rotatiting file handler for keeps the files not so big and backups maxbytes tells how many 
    chars to store and backupCount tell how may files to keeps as backup '''
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    ''' formatting example '''
    ''' 2020-08-16 12:21:18,262 INFO: Microblog startup [in /home/dvm/Documents/Code/Microblog/app/__init__.py:38] '''
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

''' Setting up a mail logging system '''
if app.config['MAIL_SERVER']:
    auth = None
    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        auth = (app.config['MAIL_USERNAME'],app.config['MAIL_PASSWORD'])
    secure = ()
    mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'],app.config['MAIL_PORT']),
        fromaddr='no-reply@'+ app.config['MAIL_SERVER'],
        toaddrs=app.config['ADMINS'], subject='Microblog Server Failure',
        credentials=auth,secure=secure)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    #return 'ml'
