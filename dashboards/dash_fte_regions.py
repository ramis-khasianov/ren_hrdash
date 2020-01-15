import os
import pandas as pd
from datetime import datetime, timedelta
import json
import locale
import sys
import random

from flask_login import current_user

from dash import Dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from dashboards.dash_functions import apply_layout_with_auth, create_toolip
from dashboards.dash_configs import layout, engine, colors_le, tooltip_text

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

url_base = '/dash/dashfteregions/'


def input_to_list(input_value):
    if isinstance(input_value, dict):
        return [input_value['value']]
    if not isinstance(input_value, list):
        return [input_value]
    else:
        return input_value


dates_list = sorted(list(
    pd.read_sql('SELECT DISTINCT month_start FROM hc_data_main',
                con=engine, parse_dates=['month_start'])['month_start'].dropna()))
dates_marks = {i: "" for i in range(len(dates_list))}
dates_slider = dcc.RangeSlider(
    id='dates_slider',
    value=[len(dates_list) - 13, len(dates_list) - 1],
    min=0,
    max=len(dates_list),
    className="dcc_control"
)

n_function_show_slider = dcc.Slider(
    id='n_functions_show_slider',
    value=10,
    min=0,
    max=40,
    className='dcc_control'
)

le_list = list(pd.read_sql('''
SELECT DISTINCT legal_entity_short
FROM hc_data_main
''', con=engine)['legal_entity_short'])
le_options = [{'label': str(dept), 'value': str(dept)} for dept in le_list]
le_checklist = dcc.Checklist(
    id='le_checklist',
    options=le_options,
    value='ГРС',
    className='dcc_control',
    labelStyle={'display': 'block'}
)

le_dict = pd.read_sql('SELECT DISTINCT legal_entity_short_eng, legal_entity_short FROM hc_data_main',
                      con=engine).set_index('legal_entity_short_eng').to_dict()['legal_entity_short']
le_options_dict = [{'label': str(value), 'value': str(key)} for key, value in le_dict.items()]

le_dropdown = dcc.Dropdown(
    id='le_dropdown',
    options=le_options_dict,
    multi=True,
    value=['grs', 'medcorp', 'inrosmed', 'renprime', 'holdingrs', 'renconsult', 'renfinance'],
    className='dcc_control'
)

le_radio = dcc.RadioItems(
    id='le_radio',
    options=[
        {'label': 'Все', 'value': 'all'},
        {'label': 'Все активные', 'value': 'active'},
        {'label': 'Только ГРС', 'value': 'grs_only'},
        {'label': 'Только РЗ', 'value': 'rz_only'},
    ],
    value='all',
    labelStyle={'display': 'inline-block'},
    className='dcc_control'
)

functions_list = sorted(list(
    pd.read_sql('SELECT DISTINCT function FROM hc_data_main',
                con=engine)['function'].dropna()))
functions_options = [{'label': str(item), 'value': str(item)} for item in functions_list]
functions_dropdown = dcc.Dropdown(
    id='functions_dropdown',
    options=functions_options + [{'label': 'Все функции', 'value': 'all'}],
    multi=True,
    value='all',
    className='dcc_control'
)

cities_list = sorted(list(
    pd.read_sql('SELECT DISTINCT city FROM hc_data_main',
                con=engine)['city'].dropna()))
cities_options = [{'label': str(item), 'value': str(item)} for item in cities_list]
cities_dropdown = dcc.Dropdown(
    id='cities_dropdown',
    options=cities_options + [{'label': 'Все города', 'value': 'all'}],
    multi=True,
    value='all',
    className='dcc_control'
)

divisions_list = sorted(list(
    pd.read_sql('SELECT DISTINCT division_asc FROM hc_data_main',
                con=engine)['division_asc'].dropna()))
divisions_options = [{'label': str(item), 'value': str(item)} for item in divisions_list]
divisions_dropdown = dcc.Dropdown(
    id='divisions_dropdown',
    options=divisions_options + [{'label': 'Все дивизионы', 'value': 'all'}],
    multi=True,
    value='all',
    className='dcc_control'
)

branches_list = sorted(list(
    pd.read_sql('SELECT DISTINCT branch_asc FROM hc_data_main',
                con=engine)['branch_asc'].dropna()))
branches_options = [{'label': str(item), 'value': str(item)} for item in branches_list]
branches_dropdown = dcc.Dropdown(
    id='branches_dropdown',
    options=branches_options  + [{'label': 'Все бранчи', 'value': 'all'}],
    multi=True,
    value='all',
    className='dcc_control'
)

wf_type_radio = dcc.RadioItems(
    id='wf_type_radio',
    options=[
        {'label': 'Топ N изменений', 'value': 'top_n'},
        {'label': 'По выбранным функциям', 'value': 'selected_functions'},
    ],
    value='top_n',
    labelStyle={'display': 'inline-block'},
    className='dcc_control'
)

regions_radio = dcc.RadioItems(
    id='regions_radio',
    options=[
        {'label': 'Все сотрудники', 'value': 'all'},
        {'label': 'Выбранные дивизионы', 'value': 'by_divisions'},
        {'label': 'Выбраные города', 'value': 'by_cities'},
        {'label': 'Выбраные бранчи', 'value': 'by_branches'},
        {'label': 'Настроить', 'value': 'by_custom'},
    ],
    value='by_divisions',
    labelStyle={'display': 'inline-block'},
    className='dcc_control'
)

functions_radio = dcc.RadioItems(
        id="functions_radio",
        options=[
            {"label": "Все функции", "value": "all"},
            {"label": "Выбранные функции", "value": 'include'},
            {"label": "Кроме выбранных", "value": 'exclude'},
        ],
        value="all",
        labelStyle={"display": "inline-block"},
        className="dcc_control"
    )

pivot_functions_first = dcc.Checklist(
    id='pivot_functions_first',
    options=[
        {'label': 'Функции в начало таблицы', 'value': 'pivot_functions_first'},
    ],
    value=[]
)

pivot_include_branches = dcc.Checklist(
    id='pivot_include_branches',
    options=[
        {'label': 'Детализация таблицы по бранчу', 'value': 'pivot_include_branches'},
    ],
    value=[]
)

graph_show_totals = dcc.Checklist(
    id='graph_show_totals',
    options=[
        {'label': 'Показать ГРС полностью', 'value': 'graph_show_totals'},
    ],
    value=[]
)

layout = html.Div([
    html.Div([
        html.Div([
            html.Div(id='selected_dates_text', className="control_label"),
            dates_slider,
            regions_radio,
            html.Div([divisions_dropdown], id='divisions_dropdown_container', style={'display': 'block'}),
            html.Div([cities_dropdown], id='cities_dropdown_container', style={'display': 'block'}),
            html.Div([pivot_include_branches], id='pivot_include_branches_container', style={'display': 'block'}),
            html.Div([branches_dropdown], id='branches_dropdown_container', style={'display': 'block'}),
            functions_radio,
            html.Div([functions_dropdown], id='functions_dropdown_container', style={'display': 'block'}),
            pivot_functions_first
        ], className='pretty_container four columns'),
        html.Div([
            graph_show_totals,
            dcc.Graph(id='fte_regions_graph'),
        ], className='pretty_container eight columns'),
    ], className="row flex_display"),
    html.Div([
        html.Div(id='fte_table_container')
    ], className="pretty_container")
])


def register_dash(server):
    external_stylesheets = [
        {
            'href': '../../static/build/css/dash_styles.css',
            'rel': 'stylesheet'
        },
        {
            'href': '../../static/vendors/font-awesome/css/font-awesome.min.css',
            'rel': 'stylesheet'
        },
    ]
    app = Dash(server=server, url_base_pathname=url_base, external_stylesheets=external_stylesheets)
    apply_layout_with_auth(app, layout)

    @app.callback(
        Output(component_id='divisions_dropdown_container', component_property='style'),
        [Input(component_id='regions_radio', component_property='value')])
    def show_hide_divisions_dropdown(radio_value):
        if radio_value in ['by_custom', 'by_divisions']:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output(component_id='cities_dropdown_container', component_property='style'),
        [Input(component_id='regions_radio', component_property='value')])
    def show_hide_cities_dropdown(radio_value):
        if radio_value in ['by_custom', 'by_cities']:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output(component_id='pivot_include_branches_container', component_property='style'),
        [Input(component_id='regions_radio', component_property='value')])
    def show_hide_cities_dropdown(radio_value):
        if radio_value in ['by_custom']:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output(component_id='branches_dropdown_container', component_property='style'),
        [Input(component_id='regions_radio', component_property='value'),
         Input(component_id='pivot_include_branches', component_property='value')])
    def show_hide_branches_dropdown(radio_value, if_pivot_include_branches):
        if_pivot_include_branches = 'pivot_include_branches' in input_to_list(if_pivot_include_branches)
        if radio_value in ['by_branches'] or (radio_value in ['by_custom'] and if_pivot_include_branches):
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(Output('selected_dates_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_selected_dates_text(dates_range):
        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        text_string = 'Данные за период: {}'.format(
            str(datetime.strftime(start_date, '%b %Y')) +
            " - " +
            str(datetime.strftime(end_date, '%b %Y')))
        return text_string

    @app.callback(
        Output("functions_dropdown", "value"),
        [Input("functions_radio", "value")]
    )
    def selection_drop(selected_radio):
        if selected_radio == "all":
            return 'all'
        return 'all'

    @app.callback(
        Output('fte_table_container', 'children'),
        [Input('dates_slider', 'value'),
         Input('regions_radio', 'value'),
         Input('divisions_dropdown', 'value'),
         Input('cities_dropdown', 'value'),
         Input('branches_dropdown', 'value'),
         Input('functions_radio', 'value'),
         Input('functions_dropdown', 'value'),
         Input('pivot_functions_first', 'value'),
         Input('pivot_include_branches', 'value')
         ])
    def get_fte_table(dates_range, regions_radio_value, divisions_selected, cities_selected,
                      branches_selected, functions_radio_value, functions_selected,
                      if_pivot_functions_first, if_pivot_include_branches):
        if_pivot_functions_first = 'pivot_functions_first' in input_to_list(if_pivot_functions_first)
        if_pivot_include_branches = 'pivot_include_branches' in input_to_list(if_pivot_include_branches)
        if 'all' in input_to_list(divisions_selected):
            divisions_selected = divisions_list
        if 'all' in input_to_list(cities_selected):
            cities_selected = cities_list;
        if 'all' in input_to_list(branches_selected):
            branches_selected = branches_list
        if 'all' in input_to_list(functions_selected):
            functions_selected = functions_list;

        df_raw = pd.read_sql(
            '''
            SELECT
                legal_entity_short_eng,
                division_asc,
                branch_asc,
                city,
                function,
                month_start,
                SUM(fte) AS fte
            FROM 
                hc_data_main
            GROUP BY
                legal_entity_short_eng,
                division_asc,
                branch_asc,
                city,
                month_start,
                function
            ''',
            con=engine
        )

        df = df_raw[df_raw['legal_entity_short_eng'] == 'grs'].copy()
        group_fields = ['month_start']
        if regions_radio_value == 'by_divisions':
            df = df[df['division_asc'].isin(input_to_list(divisions_selected))]
            group_fields = ['month_start', 'division_asc']
        elif regions_radio_value == 'by_cities':
            df = df[df['city'].isin(input_to_list(cities_selected))]
            group_fields = ['month_start', 'city']
        elif regions_radio_value == 'by_branches':
            df = df[df['branch_asc'].isin(input_to_list(branches_selected))]
            group_fields = ['month_start', 'branch_asc']
        elif regions_radio_value == 'by_custom':
            if if_pivot_include_branches:
                df = df[
                    df['division_asc'].isin(input_to_list(divisions_selected)) &
                    df['city'].isin(input_to_list(cities_selected)) &
                    df['branch_asc'].isin(input_to_list(branches_selected))
                ]
                group_fields = ['month_start', 'division_asc', 'city', 'branch_asc']
            else:
                df = df[
                    df['division_asc'].isin(input_to_list(divisions_selected)) &
                    df['city'].isin(input_to_list(cities_selected))
                    ]
                group_fields = ['month_start', 'division_asc', 'city']
        else:
            pass

        if functions_radio_value == 'include':
            df = df[df['function'].isin(input_to_list(functions_selected))]
            if if_pivot_functions_first:
                group_fields = ['function'] + group_fields
            else:
                group_fields = group_fields + ['function']
        elif functions_radio_value == 'exclude':
            df = df[~df['function'].isin(input_to_list(functions_selected))]
            if if_pivot_functions_first:
                group_fields = ['function'] + group_fields
            else:
                group_fields = group_fields + ['function']
        else:
            pass

        end_date = dates_list[dates_range[1] - 1]
        start_date = dates_list[dates_range[1] - 13]

        df = df[(df['month_start'] >= start_date) & (df['month_start'] <= end_date)]
        dff = df.groupby(group_fields).agg(fte=('fte', 'sum')).reset_index()

        pivot_group_columns = [x for x in group_fields if x != 'month_start']
        dff['period'] = dff['month_start'].dt.strftime('%Y_%m')
        dff['fte'] = dff['fte'].round(1)
        dff_result = pd.pivot_table(
            dff,
            index=pivot_group_columns,
            columns='period',
            values='fte',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        col_names = {
            'division_asc': 'Дивизион',
            'branch_asc': 'Бранч',
            'city': 'Город',
            'function': 'Функция',
            'index': 'Всего'
        }
        table_columns = []
        cell_conditionals = []
        for col in dff_result.columns:
            col_dict = {}
            if col in ['function']:
                cond_dict = {'if': {'column_id': f'{col}'}, 'textAlign': 'left', 'width': '20%'}
            else:
                cond_dict = {'if': {'column_id': f'{col}'}, 'textAlign': 'left'}
            if col in col_names.keys():
                col_dict['name'] = col_names[col]
                col_dict['id'] = col
            else:
                col_dict['name'] = datetime.strftime(datetime(int(col[:4]), int(col[-2:]), 1), '%b').title()
                col_dict['id'] = col
            table_columns.append(col_dict)
            cell_conditionals.append(cond_dict)

        data = dff_result.to_dict('records')
        result_table = dash_table.DataTable(
            data=data,
            id='detailed_function_table',
            columns=table_columns,
            style_as_list_view=True,
            fixed_rows={'headers': True, 'data': 0},
            style_cell={
                'backgroundColor': '#EDEDED',
                'textOverflow': 'ellipsis',
            },
            style_cell_conditional=cell_conditionals
        )
        return result_table

    @app.callback(
        Output('fte_regions_graph', 'figure'),
        [Input('dates_slider', 'value'),
         Input('regions_radio', 'value'),
         Input('divisions_dropdown', 'value'),
         Input('cities_dropdown', 'value'),
         Input('branches_dropdown', 'value'),
         Input('functions_radio', 'value'),
         Input('functions_dropdown', 'value'),
         Input('pivot_functions_first', 'value'),
         Input('pivot_include_branches', 'value'),
         Input('graph_show_totals', 'value'),
         ])
    def get_fte_table(dates_range, regions_radio_value, divisions_selected, cities_selected,
                      branches_selected, functions_radio_value, functions_selected,
                      if_pivot_functions_first, if_pivot_include_branches, if_graph_show_totals):
        if_pivot_functions_first = 'pivot_functions_first' in input_to_list(if_pivot_functions_first)
        if_pivot_include_branches = 'pivot_include_branches' in input_to_list(if_pivot_include_branches)
        if_graph_show_totals = 'graph_show_totals' in input_to_list(if_graph_show_totals)
        if 'all' in input_to_list(divisions_selected):
            divisions_selected = divisions_list
        if 'all' in input_to_list(cities_selected):
            cities_selected = cities_list;
        if 'all' in input_to_list(branches_selected):
            branches_selected = branches_list
        if 'all' in input_to_list(functions_selected):
            functions_selected = functions_list;

        df_raw = pd.read_sql(
            '''
            SELECT
                legal_entity_short_eng,
                division_asc,
                branch_asc,
                city,
                function,
                month_start,
                SUM(fte) AS fte
            FROM 
                hc_data_main
            GROUP BY
                legal_entity_short_eng,
                division_asc,
                branch_asc,
                city,
                month_start,
                function
            ''',
            con=engine
        )

        df = df_raw[df_raw['legal_entity_short_eng'] == 'grs'].copy()
        df_total = df.groupby('month_start').agg(fte=('fte', 'sum')).reset_index()

        group_fields = ['month_start']
        if regions_radio_value == 'by_divisions':
            df = df[df['division_asc'].isin(input_to_list(divisions_selected))]
            group_fields = ['month_start', 'division_asc']
        elif regions_radio_value == 'by_cities':
            df = df[df['city'].isin(input_to_list(cities_selected))]
            group_fields = ['month_start', 'city']
        elif regions_radio_value == 'by_branches':
            df = df[df['branch_asc'].isin(input_to_list(branches_selected))]
            group_fields = ['month_start', 'branch_asc']
        elif regions_radio_value == 'by_custom':
            df = df[
                df['division_asc'].isin(input_to_list(divisions_selected)) &
                df['city'].isin(input_to_list(cities_selected)) &
                df['branch_asc'].isin(input_to_list(branches_selected))
                ]
            group_fields = ['month_start', 'division_asc', 'city', 'branch_asc']
        else:
            pass

        if functions_radio_value == 'include':
            df = df[df['function'].isin(input_to_list(functions_selected))]
            if if_pivot_functions_first:
                group_fields = ['function'] + group_fields
            else:
                group_fields = group_fields + ['function']
        elif functions_radio_value == 'exclude':
            df = df[~df['function'].isin(input_to_list(functions_selected))]
            if if_pivot_functions_first:
                group_fields = ['function'] + group_fields
            else:
                group_fields = group_fields + ['function']
        else:
            pass

        end_date = dates_list[dates_range[1] - 1]
        start_date = dates_list[dates_range[1] - 13]

        dff = df.groupby(group_fields).agg(fte=('fte', 'sum')).reset_index()
        dff = dff.groupby('month_start').agg(fte=('fte', 'sum')).reset_index()

        dff['fte'] = dff['fte'].round(1)
        trace_current = go.Bar(
            x=dff['month_start'],
            y=dff['fte'],
            name='Выбранные',
            marker={
                'color': '#519E8A'
            }
        )

        if if_graph_show_totals:
            trace_total = go.Bar(
                x=df_total['month_start'],
                y=df_total['fte'],
                name='ГРС',
                marker={
                    'color': '#2A3F54'
                }
            )
        xaxis_range = [dates_list[-24] + timedelta(days=15),
                       dates_list[-1] + timedelta(days=15)]
        fte_graph_layout = go.Layout(
            title_text="Динамика численности ГРС",
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            legend=dict(font=dict(size=10), orientation="h"),
            xaxis=dict(range=xaxis_range, tickformat='%m.%Y', nticks=12),
        )
        if if_graph_show_totals:
            figure = {'data': [trace_current, trace_total], 'layout': fte_graph_layout}
        else:
            figure = {'data': [trace_current], 'layout': fte_graph_layout}
        return figure

    return app.server
