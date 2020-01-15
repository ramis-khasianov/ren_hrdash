from flask import Blueprint
from flask import render_template
from flask_login import login_required
from app.base.models import User
from app.posts.models import Post, PlannedFeature
from app.settings.models import LegalEntity, Function, CostCenter, Location, Branch, Division, AccessSetting

blueprint = Blueprint(
    'settings_blueprint',
    __name__,
    url_prefix='/settings',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/edit_posts')
@login_required
def edit_posts():
    posts = Post.query.order_by(Post.date.desc()).all()
    features = PlannedFeature.query.order_by(PlannedFeature.feature_planned_end.asc()).all()
    return render_template('edit_posts.html', posts=posts, features=features)


@blueprint.route('/edit_users')
@login_required
def edit_users():
    users = User.query.order_by(User.date_added.desc()).all()
    access_settings = AccessSetting.query.all()
    return render_template('edit_users.html', users=users, access_settings=access_settings)


@blueprint.route('/edit_refs')
@login_required
def edit_refs():
    legal_entities = LegalEntity.query.order_by(LegalEntity.legal_entity_code.asc()).all()
    functions = Function.query.order_by(Function.function.asc()).all()
    cost_centers = CostCenter.query.order_by(CostCenter.cost_center.asc()).all()
    locations = Location.query.order_by(Location.location.asc()).all()
    branches = Branch.query.order_by(Branch.branch.asc()).all()
    divisions = Division.query.order_by(Division.division.asc()).all()
    return render_template('edit_refs.html', legal_entities=legal_entities,
                           functions=functions, cost_centers=cost_centers,
                           locations=locations, branches=branches, divisions=divisions)
