import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.path.join(os.environ['DB_URI'], 'hrdashboard' + '?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN = {'email': 'rkhasyanov@renins.com'}
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
