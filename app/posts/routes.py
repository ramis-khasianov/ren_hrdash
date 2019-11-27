from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required

from app import db
from app.posts.forms import PostForm
from app.posts.models import Post

blueprint = Blueprint(
    'posts_blueprint',
    __name__,
    url_prefix='/posts',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/create',methods=['GET','POST'])
@login_required
def create_post():  # todo: check if only available to admin
    form = PostForm()

    if form.validate_on_submit():

        blog_post = Post(title=form.title.data,
                         text=form.text.data,
                         user_id=current_user.id
                         )
        db.session.add(blog_post)
        db.session.commit()
        return redirect(url_for('settings_blueprint.administration'))

    return render_template('create_post.html', form=form)


@blueprint.route("/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    blog_post = Post.query.get_or_404(post_id)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect(url_for('settings_blueprint.administration'))
