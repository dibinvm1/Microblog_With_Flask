from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegristrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',title = "Home Page", posts = posts)

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.uName.data.lower()) |(User.email == form.uName.data.lower())).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or Password')
            return redirect(url_for('login'))
        login_user(user,remember=form.rememberMe.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title = 'Sign In', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register',methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegristrationForm()
    if form.validate_on_submit():
        user = User(username = form.uName.data.lower(),email = form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations,You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    usr = User.query.filter_by(username=username).first_or_404()
    posts = [
        {
            'author': usr,
            'body': 'Test POST!!!!!!1'
        },
        {
            'author': usr,
            'body': 'Test POST!!!!!!2'
        }
    ]
    return render_template('user.html', user=usr, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.uName.data.lower()
        current_user.about_me = form.aboutMe.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method ==  'GET':
        form.uName.data = current_user.username
        form.aboutMe.data = current_user.about_me
    return render_template('edit_profile.html',title='Edit Profile', form=form)