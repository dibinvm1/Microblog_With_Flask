from flask_mail import Message
from flask_babel import _
from flask import current_app
from app import mail
from threading import Thread


def send_mail(subject, sender, recipients, text_body, html_body):
    ''' sending mail prototype 
        html and text body needed as the body of the message'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    msg.body  = text_body
    #mail.send(msg)
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
        