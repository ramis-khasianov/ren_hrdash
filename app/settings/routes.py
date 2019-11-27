from flask import Blueprint
from flask import render_template
from app.base.models import User
from app.posts.models import Post

blueprint = Blueprint(
    'settings_blueprint',
    __name__,
    url_prefix='/settings',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/administration')
def administration():
    users = User.query.order_by(User.email.desc()).all()
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('administration.html', users=users, posts=posts)
