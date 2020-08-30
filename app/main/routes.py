from app import  db
from flask import render_template, flash, redirect, url_for, request, g, current_app
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, MessageForm, CommentForm
from flask_login import current_user, login_user, login_required
from app.models import User, Post, Message, Comment
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language
from app.main import bp


# for Date time 
@bp.before_app_request
def before_request():
    ''' Used for adding the last scene to user invoked for every request 
        also used to request the locale for translating'''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    ''' index page 
     returns the renderd template for index page'''
    form = PostForm()
    commentForm = CommentForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5 :
            language =''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)        
    posts = current_user.followed_posts().paginate(
        page,current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.index',page = posts.next_num) \
         if posts.has_next else None
    prev_url = url_for('main.index',page = posts.prev_num) \
         if posts.has_prev else None
    return render_template('index.html',title = _("Home Page"), form=form, posts = posts.items, 
                            next_url=next_url, prev_url=prev_url, commentForm=commentForm)


@bp.route('/user/<username>')
@login_required
def user(username):
    ''' User profile page 
     returns the renderd template for profile page'''
    usr = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)

    posts = Post.query.filter_by(author = usr).order_by(Post.timestamp.desc()).paginate(
        page,current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.user', username=usr.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=usr.username, page=posts.prev_num) if posts.has_prev else None

    form = EmptyForm()
    commentForm = CommentForm()
    return render_template('user.html', user=usr, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form, commentForm=commentForm)


@bp.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    ''' User Edit profile page 
     returns the renderd template for edit profile page'''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.uName.data.lower()
        current_user.about_me = form.aboutMe.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method ==  'GET':
        form.uName.data = current_user.username
        form.aboutMe.data = current_user.about_me
    return render_template('edit_profile.html',title=_('Edit Profile'), form=form)



@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    ''' Follow call invokes when user clicks follow button in a user profile page 
     returns the renderd template for same user profile page'''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    ''' UnFollow call invokes when user clicks unfollow in a user profile page 
     returns the renderd template for same user profile page'''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    ''' Explore call invokes when user clicks explore button in the Nav bar 
     returns the renderd template for index page with all the post fro all users'''
    form = EmptyForm()
    commentForm = CommentForm()
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.explore',page = posts.next_num)\
         if posts.has_next else None
    prev_url = url_for('main.explore',page = posts.prev_num)\
         if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, 
                            next_url=next_url, prev_url=prev_url, delform=form, commentForm=commentForm)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    try:
        posts, total = Post.search(g.search_form.query.data, page,current_app.config['POSTS_PER_PAGE'])
    except:
        return redirect(url_for('main.explore'))
    next_url = url_for('main.search', q=g.search_form.query.data, page=page + 1) \
            if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.query.data, page=page - 1) \
            if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    usr = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=usr, form=form)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    rec = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=rec,
        body = form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_('Message has been sent'))
        return redirect(url_for('main.user',username=recipient))
    return render_template('send_message.html', title=_('Send Message'),form = form, recipient = recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    msgs = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('mian.messages', page=msgs.next_num) if msgs.has_next else None
    prev_url = url_for('mian.messages', page=msgs.prev_num) if msgs.has_prev else None
    return render_template('messages.html', messages=msgs.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/deletePost/<id>', methods= ['GET', 'POST'])
@login_required
def deletePost(id):
    post = Post.query.filter_by(id=id).first_or_404()
    if current_user != post.author:
        flash("curiosity killed the cat")
        return redirect(url_for('main.index'))
    form = EmptyForm()
    prev_page = request.referrer
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash(_("The post has been deleted"))
        return redirect(prev_page)


@bp.route('/deleteComment/<id>', methods= ['GET', 'POST'])
@login_required
def deleteComment(id):
    comment = Comment.query.filter_by(id=id).first_or_404()
    if current_user != comment.commentAuthor:
        flash("curiosity killed the cat")
        return redirect(url_for('main.index'))
    form = EmptyForm()
    prev_page = request.referrer
    if form.validate_on_submit():
        db.session.delete(comment)
        db.session.commit()
        flash(_("The Comment has been deleted"))
        return redirect(prev_page)


@bp.route('/postComment/<id>', methods= ['GET', 'POST'])
@login_required
def postComment(id):
    commentForm = CommentForm()
    if commentForm.validate_on_submit():
        language = guess_language(commentForm.body.data)
        if language == 'UNKNOWN' or len(language) > 5 :
            language =''
        comment = Comment(body=commentForm.body.data, commentAuthor=current_user, language=language, post_id = id)
        db.session.add(comment)
        db.session.commit()
        flash(_("The Comment is now live"))
        return redirect(request.referrer)
    return redirect(url_for('main.index'))

