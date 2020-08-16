from flask_mail import Message
from flask import render_template
from flask_babel import _
from app import app, mail
from threading import Thread


def send_mail(subject, sender, recipients, text_body, html_body):
    ''' sending mail prototype 
        html and text body needed as the body of the message'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    msg.body  = text_body
    #mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()
    

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_password_reset_email(user):
    ''' sending mail to reset the password 
     jwt token is generated send with the mail'''
    token = user.get_reset_password_token()
    send_mail(_('[Microblog] Reset Your Password'), sender=app.config['ADMINS'][0],
    recipients=[user.email],
    text_body=render_template('email/reset_password.txt', user=user,token=token ),
    html_body=render_template('email/reset_password.html', user=user, token=token))
 
    