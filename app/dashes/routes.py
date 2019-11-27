from flask import Blueprint, render_template
from dashboards.dash_fte import url_base as url_dash_fte
from dashboards.dash_turnover import url_base as url_dash_turnover
from dashboards.dash_demography import url_base as url_dash_demography

blueprint = Blueprint(
    'dashes_blueprint',
    __name__,
    url_prefix='/dashes',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/dash_fte')
def dash_fte():
    return render_template('dash_fte.html', dash_url=url_dash_fte)


@blueprint.route('/dash_turnover')
def dash_turnover():
    return render_template('dash_turnover.html', dash_url=url_dash_turnover)


@blueprint.route('/dash_demography')
def dash_demography():
    return render_template('dash_demography.html', dash_url=url_dash_demography)