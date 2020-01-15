from flask import Blueprint, render_template
from flask_login import current_user, login_required
from app.base.models import HomeMetrics
from app.posts.models import Post, PlannedFeature, Vote, Voting, VotingOption
from app import db


blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix='/home',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/')
def index():
    max_date = db.session.query(db.func.max(HomeMetrics.report_date)).first()[0]
    metrics = HomeMetrics.query.filter_by(report_date=max_date).all()
    features = PlannedFeature.query.order_by(PlannedFeature.feature_planned_end.asc()).limit(6).all()

    result_metrics = {}
    for metric in metrics:
        key = metric.metric_name
        values = dict(
            value=metric.value,
            report_date=metric.report_date,
            report_period_start=metric.report_period_start,
            report_period_end=metric.report_period_end
        )
        result_metrics[key] = values
    posts = Post.query.order_by(Post.date.desc()).limit(4).all()
    try:
        print()
    except AttributeError:
        pass
    return render_template('index.html', posts=posts, metrics=result_metrics, features=features)



