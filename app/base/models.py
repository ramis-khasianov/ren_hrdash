from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=True)
    comment = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), default=4)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    role = db.relationship('Role', backref='role_member', lazy=True)

    access_settings = db.relationship('AccessSetting', backref='user', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return str(self.email)

    def get_id(self):
        return self.user_id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):

    __tablename__ = 'roles'

    role_id = db.Column(db.Integer, primary_key=True)
    name_eng = db.Column(db.String(64))
    name_rus = db.Column(db.String(64))
    description = db.Column(db.String(128))

    def __init__(self, name_eng, name_rus, description):
        self.name_eng = name_eng
        self.name_rus = name_rus
        self.description = description

    def __repr__(self):
        return str(self.name_eng)


class HomeMetrics(db.Model):

    __tablename__ = 'home_metrics'

    metric_id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(64))
    value = db.Column(db.String(64))
    report_date = db.Column(db.DateTime)
    report_period_start = db.Column(db.DateTime)
    report_period_end = db.Column(db.DateTime)

    def __init__(self, metric_id, metric_name, value, report_date, report_period_start, report_period_end):

        self.metric_id = metric_id
        self.metric_name = metric_name
        self.value = value
        self.report_date = report_date
        self.report_period_start = report_period_start
        self.report_period_end = report_period_end

    def __repr__(self):
        return str(self.metric_name) + " as of " + str(self.report_date)


