from flask import Blueprint, render_template
from datetime import date
from app.posts.models import Post

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='/home',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/')
def index():
    posts = Post.query.order_by(Post.date.desc()).limit(4).all()
    return render_template('index.html', posts=posts)
