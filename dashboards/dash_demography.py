import os
import pandas as pd
from datetime import datetime
import json
import locale
import sys
import random

from flask_login import current_user

from dash import Dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from dashboards.dash_functions import apply_layout_with_auth
from dashboards.dash_configs import layout, engine, colors_le

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

url_base = '/dash/dashdemography/'

dates_list = sorted(list(
    pd.read_sql('SELECT DISTINCT month_start FROM hc_data_main',
                con=engine, parse_dates=['month_start'])['month_start'].dropna()))
dates_marks = {i: "" for i in range(len(dates_list))}
dates_slider = dcc.Slider(
    id='dates_slider',
    value=len(dates_list),
    min=0,
    max=len(dates_list),
    className="dcc_control"
)

le_dict = pd.read_sql('SELECT DISTINCT legal_entity_short_eng, legal_entity_short FROM hc_data_main',
                      con=engine).set_index('legal_entity_short_eng').to_dict()['legal_entity_short']
le_options = [{'label': str(value), 'value': str(key)} for key, value in le_dict.items()]

le_dropdown = dcc.Dropdown(
        id='le_dropdown',
        options=le_options,
        multi=True,
        value=['grs'],
        className='dcc_control'
)

cities_list = sorted(list(
    pd.read_sql('SELECT DISTINCT city FROM hc_data_main',
                con=engine)['city'].dropna()))
cities_options = [{'label': str(item), 'value': str(item)} for item in cities_list]

lines_list = sorted(list(
    pd.read_sql('SELECT DISTINCT line FROM hc_data_main',
                con=engine)['line'].dropna()))
lines_options = [{'label': str(item), 'value': str(item)} for item in lines_list]

lines_checklist = dcc.Checklist(
    id='lines_checklist',
    options=lines_options,
    value=lines_list,
    className='dcc_control'
)

functions_list = sorted(list(
    pd.read_sql('SELECT DISTINCT function FROM hc_data_main',
                con=engine)['function'].dropna()))
functions_options = [{'label': str(item), 'value': str(item)} for item in functions_list]

functions_radio = dcc.RadioItems(
        id="functions_radio",
        options=[
            {"label": "Все", "value": "all"},
            {"label": "Выбранные", "value": 'include'},
            {"label": "Кроме выбранных", "value": 'exclude'},
        ],
        value="all",
        labelStyle={"display": "inline-block"},
        className="dcc_control"
    )

functions_dropdown = dcc.Dropdown(
    id='functions_dropdown',
    options=functions_options,
    multi=True,
    value=functions_list[:3],
    className='dcc_control'
)

layout = html.Div([
    html.Div([
        html.Div([
            html.Div(
                id='selected_month',
                className="control_label"
            ),
            dates_slider,
            html.P(
                    "Отобрать по линиям",
                    className="control_label"),
            lines_checklist,
            html.P(
                "Отобрать по Юр. лицам",
                className="control_label"),
            le_dropdown,
            html.P(
                "Отобрать по функциям",
                className="control_label"),
            functions_radio,
            functions_dropdown
        ], className='pretty_container three columns'),
        html.Div([
            dcc.Graph(id='functions_age_graph')
        ], className='pretty_container nine columns'),
    ], className='row flex_display'),
])


def register_dash(server):
    external_stylesheets = [
        {
            'href': '../../static/build/css/dash_styles.css',
            'rel': 'stylesheet'
        }
    ]
    app = Dash(server=server, url_base_pathname=url_base, external_stylesheets=external_stylesheets)
    apply_layout_with_auth(app, layout)

    @app.callback(Output('selected_month', 'children'),
                  [Input('dates_slider', 'value')])
    def get_current_fte_text(dates_range):
        current_date = dates_list[dates_range - 1]
        period_text = "Данные на " + datetime.strftime(current_date, '%B %Y')
        return period_text

    @app.callback(
        Output('functions_dropdown', 'value'),
        [Input('functions_radio', 'value')]
    )
    def selection_drop(selected_radio):
        if selected_radio == 'all':
            return 'Все'
        return functions_list[:7]

    @app.callback(
        Output('functions_age_graph', 'figure'),
        [Input('dates_slider', 'value'),
         Input('le_dropdown', 'value'),
         Input('lines_checklist', 'value'),
         Input('functions_dropdown', 'value'),
         Input('functions_radio', 'value')]
    )
    def get_age_graph(dates_range, selected_le, selected_lines, selected_functions, selected_func_radio):
        current_date = dates_list[dates_range - 1]
        period = datetime.strftime(current_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT
                employee_name,
                main_employee_entry,
                function,
                line,
                legal_entity_short_eng,
                age
            FROM
                hc_data_main
            WHERE
                main_employee_entry = 1 AND
                period = "{}"
        '''.format(
            period
        ), con=engine)
        if not isinstance(selected_lines, list):
            selected_lines = [selected_lines]
        if not isinstance(selected_functions, list):
            selected_functions = [selected_functions]
        if not isinstance(selected_functions, list):
            selected_le = [selected_le]
        if selected_func_radio == 'include':
            df = df[df['line'].isin(selected_lines) &
                    df['function'].isin(selected_functions) &
                    df['legal_entity_short_eng'].isin(selected_le)]
        elif selected_func_radio == 'exclude':
            df = df[df['line'].isin(selected_lines) &
                    ~df['function'].isin(selected_functions) &
                    df['legal_entity_short_eng'].isin(selected_le)].copy()
        else:
            df = df[df['line'].isin(selected_lines) & df['legal_entity_short_eng'].isin(selected_le)]
        age_groups = [
            {'title': '18-25', 'lower_bound': 18, 'upper_bound': 25},
            {'title': '26-35', 'lower_bound': 26, 'upper_bound': 35},
            {'title': '36-45', 'lower_bound': 36, 'upper_bound': 45},
            {'title': '46+', 'lower_bound': 46, 'upper_bound': 99},
        ]
        age_groups_list = [x['title'] for x in age_groups]
        def get_age_group(age):
            for age_group in age_groups:
                if (age >= age_group['lower_bound']) and (age <= age_group['upper_bound']):
                    return age_group['title']

        df['age_group'] = df['age'].apply(lambda x: get_age_group(x))
        dff_average = df.groupby('function').agg(
            mean_age=('age', 'mean'),
            median_age=('age', 'median')
        ).reset_index()
        dff_groups = pd.pivot_table(
            df,
            index='function',
            columns='age_group',
            values='age',
            aggfunc='count',
            fill_value=0
        )
        dff = pd.merge(
            dff_average,
            dff_groups,
            on='function',
            how='left'
        )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        color_blue = 250
        for age_group in age_groups_list:
            color_blue = color_blue - 40
            fig.add_trace(go.Bar(
                x=dff['function'],
                y=dff[age_group],
                name=age_group,
                marker={
                    'color': 'rgba(20, 20, {}, 0.8)'.format(str(color_blue))
                },
            ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=dff['function'],
            y=dff['mean_age'].round(1),
            name='Средний возраст',
            mode='lines+text'
        ), secondary_y=True)
        fig.update_layout(
            title_text="Возраст по функциям",
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            barmode='stack',
            hovermode='x',
            legend=dict(font=dict(size=10), orientation="h"),
        )
        fig.update_yaxes(showgrid=False, secondary_y=True, rangemode='tozero')
        return fig

    return app.server
