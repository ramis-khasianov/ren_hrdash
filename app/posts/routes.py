from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, RadioField, FieldList, FormField

from app import db
from app.posts.forms import PostForm, FeaturePlanForm, VotingForm, VotingOptionForm, VoteRadio, VoteForm
from app.posts.models import Post, PlannedFeature, Vote, Voting, VotingOption

blueprint = Blueprint(
    'posts_blueprint',
    __name__,
    url_prefix='/posts',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():  # todo: check if only available to admin
    form = PostForm()

    if form.validate_on_submit():

        post = Post(title=form.title.data,
                    text=form.text.data,
                    user_id=current_user.id
                    )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('settings_blueprint.administration'))

    return render_template('create_post.html', form=form)


@blueprint.route("/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('settings_blueprint.administration'))


@blueprint.route('/create_feature_plan', methods=['GET', 'POST'])
@login_required
def create_feature_plan():  # todo: check if only available to admin
    form = FeaturePlanForm()

    if form.validate_on_submit():

        planned_feature = PlannedFeature(
            feature_name=form.feature_name.data,
            feature_comment=form.feature_comment.data,
            feature_planned_start=form.feature_planned_start.data,
            feature_planned_end=form.feature_planned_end.data,
        )
        db.session.add(planned_feature)
        db.session.commit()
        return redirect(url_for('settings_blueprint.administration'))

    return render_template('create_feature_plan.html', form=form)


@blueprint.route("/<int:feature_id>/delete", methods=['POST'])
@login_required
def delete_feature_plan(feature_id):
    planned_feature = PlannedFeature.query.get_or_404(feature_id)
    db.session.delete(planned_feature)
    db.session.commit()
    return redirect(url_for('settings_blueprint.administration'))


@blueprint.route('/votings_list')
@login_required
def votings_list():
    all_votings = Voting.query.order_by(Voting.date.desc()).all()
    return render_template('all_votings.html', all_votings=all_votings)


@blueprint.route('/create_voting', methods=['GET', 'POST'])
@login_required
def create_voting():
    form = VotingForm()

    if form.validate_on_submit():
        voting = Voting(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.user_id,
        )
        db.session.add(voting)
        db.session.commit()
        return redirect(url_for('posts_blueprint.votings_list'))

    return render_template('create_voting.html', form=form)


@blueprint.route('votings/<int:voting_id>/view', methods=['GET', 'POST'])
@login_required
def view_voting(voting_id):
    new_option_form = VotingOptionForm()
    voting_name = Voting.query.filter_by(voting_id=voting_id).first()
    voting_options = VotingOption.query.filter_by(voting_id=voting_id).all()
    form_rows = []
    for vo in voting_options:
        vo_dict = {'voting_option_id': vo.voting_option_id, 'title': vo.text, 'text': vo.text}
        form_rows.append(vo_dict)
    voting_form = VoteForm(fields=form_rows)
    for i in voting_form.fields:
        print(i)
    if new_option_form.validate_on_submit():
        voting_option = VotingOption(
            title=new_option_form.title.data,
            text=new_option_form.text.data,
            user_id=current_user.user_id,
            voting_id=voting_id,
        )
        db.session.add(voting_option)
        db.session.commit()
        return redirect(url_for('posts_blueprint.view_voting', voting_id=voting_id, voting_options=voting_options,
                                new_option_form=new_option_form, voting_name=voting_name, voting_form=voting_form))

    return render_template('view_voting.html', voting_id=voting_id, voting_options=voting_options,
                           new_option_form=new_option_form, voting_name=voting_name, voting_form=voting_form)


@blueprint.route('/edit_posts')
@login_required
def edit_posts():
    posts = Post.query.order_by(Post.date.desc()).all()
    features = PlannedFeature.query.order_by(PlannedFeature.feature_planned_end.asc()).all()
    return render_template('edit_posts.html', posts=posts, features=features)



