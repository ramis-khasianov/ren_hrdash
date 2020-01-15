from flask import Flask
from flask_login import current_user
from app.extensions import db, migrate, login_manager
from importlib import import_module
from config import Config
from app.base.models import User
from dashboards import dash_fte, dash_turnover, dash_demography, dash_fte_regions
import logging


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    for module_name in ('base', 'home', 'dashes', 'settings', 'posts'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_logs(app):
    # for combine gunicorn logging and flask built-in logging module
    if __name__ != "__main__":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    # endif


def create_app():
    app = Flask(__name__, static_folder='base/static')
    app.config.from_object(Config)
    register_blueprints(app)
    register_extensions(app)

    @app.context_processor
    def determine_admin():
        is_admin = (current_user.is_authenticated
                    and current_user.email == app.config['ADMIN']['email'])
        return dict(is_admin=is_admin)

    configure_logs(app)

    app = dash_fte.register_dash(app)
    app = dash_turnover.register_dash(app)
    app = dash_demography.register_dash(app)
    app = dash_fte_regions.register_dash(app)

    return app
