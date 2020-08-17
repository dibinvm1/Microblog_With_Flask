from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.models import User
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm


@bp.route('/login' , methods=['GET', 'POST'])
def login():
    ''' login page 
     returns the renderd template for index if login successfull else same page'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.uName.data.lower()) | (User.email == form.uName.data.lower())).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or Password'))
            return redirect(url_for('auth.login'))
        login_user(user,remember=form.rememberMe.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html',title = _('Sign In'), form = form)



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register',methods = ['GET', 'POST'])
def register():
    ''' new Register page 
     returns the renderd template for login page if registeration is successfull else same page'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.uName.data.lower(),email = form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations,You are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title = _('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    ''' Reset password request page 
     Sends the request mail to user email if user is found'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your password'))
            return redirect(url_for('auth.login'))
        flash(_('User Not Found.Plsease use the correct email!!'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    ''' Reset password page 
    resets the password of user if token is verfied'''
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
