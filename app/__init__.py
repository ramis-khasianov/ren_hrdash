from flask import Flask
from app.extensions import db, migrate, login_manager
from importlib import import_module
from config import Config
from app.base.models import User
from dashboards import dash_fte, dash_turnover


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    for module_name in ('base', 'home', 'dashes'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def create_app():
    app = Flask(__name__, static_folder='base/static')
    app.config.from_object(Config)
    register_blueprints(app)
    register_extensions(app)
    app = dash_fte.register_dash(app)
    app = dash_turnover.register_dash(app)
    return app
