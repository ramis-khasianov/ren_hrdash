from dash import Dash
from dash.dependencies import Input, Output
import os
import dash_core_components as dcc
import dash_html_components as html
from sqlalchemy import create_engine
from flask_login import current_user
import plotly.graph_objs as go
from dashboards.dash_functions import apply_layout_with_auth
import pandas as pd

url_base = '/dash/dashhc/'

engine = create_engine('sqlite:///' + os.path.join('C:', os.sep, 'Users', 'KhasyRa1','db_local', 'hrdata.db'))

le_list = list(pd.read_sql('''
SELECT DISTINCT data_source
FROM hc_data_main
''', con=engine)['data_source'])
le_options = [{'label': str(dept), 'value': str(dept)} for dept in le_list]
le_dropdown = dcc.Dropdown(
        id='le_dropdown',
        options=le_options,
        multi=True,
        value=le_list,
        className='dcc_control',
    )

layout = html.Div([
    le_dropdown, html.Br(), html.Br(),
    dcc.Graph(id='hc_graph', className='supergraph')
])


def register_dash(server):
    app = Dash(server=server, url_base_pathname=url_base)
    apply_layout_with_auth(app, layout)

    @app.callback(
        Output('hc_graph', 'figure'),
        [Input('le_dropdown', 'value')])
    def callback_fun(value):
        print(current_user)
        selected_le = value
        df = pd.read_sql('''
            SELECT data_source, month_start, fte FROM hc_data_main;
        ''', con=engine)
        dff = pd.pivot_table(df, index=['data_source', 'month_start'], values='fte', aggfunc='sum').reset_index()
        traces = []
        for le in dff['data_source'].unique():
            if le in selected_le:
                traces.append(go.Bar(
                    x=dff[dff['data_source'] == le]['month_start'],
                    y=dff[dff['data_source'] == le]['fte'],
                    name=le
                ))
        go_layout = go.Layout(
            title_text="Численность персонала по функциям",
            plot_bgcolor='#EDEDED',
            paper_bgcolor='#EDEDED',
            barmode='stack',
            hovermode='x'
        )
        fig = {'data': traces, 'layout': go_layout}
        return fig

    return app.server
