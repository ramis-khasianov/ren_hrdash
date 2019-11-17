from flask_login import current_user
import dash_html_components as html


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

