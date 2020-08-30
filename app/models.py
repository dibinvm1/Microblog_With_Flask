from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db , login
from flask_login import UserMixin
from flask import current_app
from hashlib import md5
from time import time
import jwt
from app.search import addToIndex, removeFromIndex, queryIndex

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = queryIndex(cls.__tablename__, expression, page, per_page)
        if total == None:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                addToIndex(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                addToIndex(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                removeFromIndex(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            addToIndex(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class User(UserMixin,db.Model):
    ''' User Table class
        contains all the columns and relations ships in the user table '''
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(64),index=True,unique = True)
    email = db.Column(db.String(120),index = True , unique = True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref = 'author' , lazy = 'dynamic')
    comments = db.relationship('Comment',backref = 'commentAuthor' , lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    followed = db.relationship(
        'User',secondary= followers,
        primaryjoin= (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers',lazy = 'dynamic'), lazy = 'dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id',
                                    backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def __repr__(self):
        ''' setting up how the instance represents '''
        return '<User {}>'.format(self.username)
    
    def set_password(self,password):
        ''' generating and setting password hash in the table '''
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        ''' checks if the password is correct by matching password hashs
        returns boolean value'''
        return check_password_hash(self.password_hash,password)
    
    def avatar(self,size):
        '''generates the avatar hash to be used in the gravatar website
        and returns the URI string'''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_following(self,user):
        ''' Checks if the current_user is following  specified user 
        returns True if current user is following specifed user else False'''
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self,user):
        ''' adds user to current_user following list '''
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self,user):
        ''' removes the user from current_user following list '''
        if self.is_following(user):
            self.followed.remove(user)
    
    def followed_posts(self):
        ''' query to get all the following users post and current_user's own past and 
        sorts them based on the timestamp descending
        returns a list of posts'''
        followed = Post.query.join(
            followers,(followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)    
        return followed.union(own).order_by(Post.timestamp.desc())
 
    def get_reset_password_token(self,expires_in=600):
        ''' generates a jwt token based on the Secret key 
        returns the token String'''
        return jwt.encode({'reset_password':self.id, 'exp':time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        ''' checks the jwt token based on the Secret key 
        returns User class instance
        This is a static method so does not need the self param and can't modify the class functionality'''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900,1,1)
        return Message.query.filter_by(recipient = self).filter(
            Message.timestamp > last_read_time).count()

class Post(SearchableMixin, db.Model):
    ''' Post Table class
        contains all the columns and relations ships in the post table '''
    __searchable__ = ['body']
    id = db.Column(db.Integer,primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default = datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    comments = db.relationship('Comment',backref = 'commentedPost' , lazy = 'dynamic')
    
    def __repr__(self):
        ''' setting up how the instance represents '''
        return '<Post {}'.format(self.body)
    
    def getComments(self):
        '''Query to get all the comments under this post '''
        return Comment.query.filter_by(post_id=self.id).order_by(Comment.timestamp.desc()).limit(5).all()
    

@login.user_loader
def load_user(id):
    ''' returns the user instance based on the user.id provided '''
    return User.query.get(int(id))


class Message(db.Model):
    ''' Message Table class
        contains all the columns and relations ships in the post table '''
    id = db.Column(db.Integer,primary_key = True)
    sender_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default = datetime.utcnow)

    def __repr__(self):
        ''' setting up how the instance represents '''
        return '<Message {}'.format(self.body)

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default = datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        ''' setting up how the instance represents '''
        return '<Comment {}'.format(self.body)