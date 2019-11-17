from flask import Blueprint
from flask import render_template

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='/home',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/')
def index():
    return render_template('index.html')