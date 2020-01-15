from flask_login import current_user
import dash_html_components as html
import dash_bootstrap_components as dbc
from dashboards import dash_configs


def create_toolip(tooltip_id, tooltip_text):
    result_div = html.Div([
        html.I(className='fa fa-question-circle container_tooltip', id=tooltip_id),
        dbc.Tooltip(tooltip_text,
                    target=tooltip_id,
                    placement='left',
                    hide_arrow=True,
                    className="control_label",
                    autohide=False,
                    style={
                        'max-width': '200px',
                        'padding': '.25rem',
                        'text-align': 'left',
                        'background-color': '#000',
                        'border-radius': '.25rem',
                        'color': '#fff',
                        'font-size': '0.7em',
                        'white-space': 'pre-wrap'
                    }),
    ])
    return result_div


def apply_layout_with_auth(app, layout):
    def serve_layout():
        if current_user and current_user.is_authenticated:
            return html.Div([
                html.Div(id='session_id', style={'display': 'none'}),
                layout
            ])
        return html.Div('403 Access Denied')

    app.config.suppress_callback_exceptions = True
    app.layout = serve_layout



