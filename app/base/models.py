from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.posts.models import Post

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return str(self.email)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class AccessCostCenter(db.Model):

    __tablename__ = 'access_cost_centers'

    users = db.relationship(User)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cost_center = db.Column(db.String(64), index=True)
    branch = db.Column(db.String(64), index=True)
    location = db.Column(db.String(64), index=True)
    division = db.Column(db.String(64), index=True)
    access_type = db.Column(db.String(64), index=True)

    def __init__(self, user_id, cost_center, branch, location, division, access_type):
        self.user_id = user_id
        self.cost_center = cost_center
        self.branch = branch
        self.location = location
        self.division = division
        self.access_type = access_type

    def __repr__(self):
        return str(self.email)

