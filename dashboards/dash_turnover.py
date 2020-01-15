import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
import locale
import sys

from flask_login import current_user

from dash import Dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from dashboards.dash_functions import apply_layout_with_auth
from dashboards.dash_configs import layout, engine, colors_groups

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

url_base = '/dash/dashturnover/'

dates_list = sorted(list(
    pd.read_sql('SELECT DISTINCT month_start FROM hc_data_main',
                con=engine, parse_dates=['month_start'])['month_start'].dropna()))
dates_marks = {i: "" for i in range(len(dates_list))}
cities_list = sorted(list(
    pd.read_sql('SELECT DISTINCT city FROM hc_data_main',
                con=engine)['city'].dropna()))
cities_options = [{'label': str(item), 'value': str(item)} for item in cities_list]
lines_list = sorted(list(
    pd.read_sql('SELECT DISTINCT line FROM hc_data_main',
                con=engine)['line'].dropna()))
lines_options = [{'label': str(item), 'value': str(item)} for item in lines_list]
functions_list = sorted(list(
    pd.read_sql('SELECT DISTINCT function FROM hc_data_main',
                con=engine)['function'].dropna()))
functions_options = [{'label': str(item), 'value': str(item)} for item in functions_list]
cc_list = sorted(list(
    pd.read_sql('SELECT DISTINCT cost_center FROM hc_data_main',
                con=engine)['cost_center'].dropna()))
cc_options = [{'label': str(item), 'value': str(item)} for item in cc_list]
le_list = sorted(list(
    pd.read_sql('SELECT DISTINCT legal_entity FROM hc_data_main',
                con=engine)['legal_entity'].dropna()))
le_options = [{'label': str(item), 'value': str(item)} for item in le_list]

dates_slider = dcc.RangeSlider(
    id='dates_slider',
    value=[len(dates_list)-13, len(dates_list)-1],
    min=0,
    max=len(dates_list),
    className="dcc_control"
)

cities_dropdown = dcc.Dropdown(
    id='cities_dropdown',
    options=cities_options,
    multi=True,
    value=cities_list,
    className='dcc_control'
)

lines_checklist = dcc.Checklist(
    id='lines_checklist',
    options=lines_options,
    value=lines_list,
    className='dcc_control'
)

functions_dropdown = dcc.Dropdown(
    id='functions_dropdown',
    options=functions_options,
    multi=True,
    value=functions_list[:3],
    className='dcc_control'
)

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

le_dropdown = dcc.Dropdown(
    id='le_dropdown',
    options=le_options,
    multi=True,
    value=le_list,
    className='dcc_control'
)


layout = html.Div([
    dcc.Store(id='memory'),
    html.Div([
        html.Div([
            html.Div(
                id='selected_dates_text',
                className="control_label"),
            dates_slider,
            html.Br(),
            html.P(
                "Отобрать по линиям",
                className="control_label"),
            lines_checklist,
            html.Br(),
            html.P(
                "Отобрать по функциям",
                className="control_label"),
            functions_radio,
            functions_dropdown,
            html.Br(),
        ], className='pretty_container four columns'),
        html.Div([
            html.Div([
                dcc.Graph(id='total_to_graph')],
                id='total_to_graph_container',
                className='pretty_container'),
        ], className='eight columns')
    ], className='row flex_display'),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='hires_attrition_graph')],
                id='hires_attrition_graph_container',
                className='pretty_container'),
        ], className='seven columns'),
        html.Div([
            html.Div([
                dcc.Graph(id='hires_attrition_pie')],
                id='hires_attrition_pie_container',
                className='pretty_container'),
        ], className='five columns'),
    ], className='row flex_display'),
    html.Div(
        id='exited_employees_table_container',
        className='pretty_container'
    ),
],
    id="main_container",
    style={"display": "flex", "flex-direction": "column"},
)


def register_dash(server):
    external_stylesheets = [
        {
            'href': '../../static/build/css/dash_styles.css',
            'rel': 'stylesheet'
        }
    ]
    app = Dash(server=server, url_base_pathname=url_base, external_stylesheets=external_stylesheets)
    apply_layout_with_auth(app, layout)

    @app.callback(
        Output('exited_employees_table_container', 'children'),
        [Input('lines_checklist', 'value'),
         Input('functions_dropdown', 'value'),
         Input('functions_radio', 'value'),
         Input('dates_slider', 'value')],
        [State('memory', 'data')])
    def get_exited_employees_table(selected_lines, selected_functions, selected_radio, dates_range, memory_data):
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')

        if memory_data is None:
            return ''
        elif memory_data['last_clicked']['id'] is None:
            return ''
        elif memory_data['last_clicked']['id'] == 'turnover':
            df = pd.read_sql('''
                        SELECT
                        month_start,
                        line,
                        function,
                        employee_name,
                        position,
                        city,
                        hire_date,
                        exit_date,
                        tenure_group_on_exit,
                        tenure_months
                        FROM hc_data_main
                        WHERE event_exit = 1
                        ORDER BY function, employee_id;
                        ''', con=engine, parse_dates=['month_start'])
        elif memory_data['last_clicked']['id'] == 'attrition':
            df = pd.read_sql('''
                        SELECT
                        month_start,
                        line,
                        function,
                        employee_name,
                        position,
                        city,
                        hire_date,
                        exit_date,
                        tenure_group_on_exit,
                        tenure_months
                        FROM hc_data_main
                        WHERE event_hire = 1
                        ORDER BY function, employee_id;
                        ''', con=engine, parse_dates=['month_start'])
        else:
            return ''

        if not isinstance(selected_lines, list):
            selected_lines = [selected_lines]
        if not isinstance(selected_functions, list):
            selected_functions = [selected_functions]

        if selected_radio == 'include':
            dff = df[df['line'].isin(selected_lines) & df['function'].isin(selected_functions)].copy()
        elif selected_radio == 'exclude':
            dff = df[df['line'].isin(selected_lines) & ~df['function'].isin(selected_functions)].copy()
        else:
            dff = df[df['line'].isin(selected_lines)].copy()
        dff = dff[(dff['month_start'] <= end_date) & (dff['month_start'] >= start_date)]
        dff['hire_date'] = dff['hire_date'].dt.strftime('%d.%m.%Y')
        dff['exit_date'] = dff['exit_date'].dt.strftime('%d.%m.%Y')
        dff['exit_date'].fillna('-', inplace=True)
        data = dff[['function',
                    'employee_name',
                    'position',
                    'city',
                    'hire_date',
                    'exit_date',
                    'tenure_group_on_exit'
                    ]].to_dict('records')
        result_table = dash_table.DataTable(
            data=data,
            style_as_list_view=True,
            id='exited_employees_table',
            fixed_rows={'headers': True, 'data': 0},
            columns=[
                {'name': 'Функция', 'id': 'function'},
                {'name': 'ФИО', 'id': 'employee_name'},
                {'name': 'Должность', 'id': 'position'},
                {'name': 'Город', 'id': 'city'},
                {'name': 'Дата приема', 'id': 'hire_date'},
                {'name': 'Дата увольнения', 'id': 'exit_date'},
                {'name': 'Группа стажа', 'id': 'tenure_group_on_exit'}
            ],
            style_cell_conditional=[
                {'if': {'column_id': 'function'},
                 'width': '20%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'employee_name'},
                 'width': '20%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'position'},
                 'width': '15%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'city'},
                 'width': '10%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'hire_date'},
                 'width': '10%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'exit_date'},
                 'width': '10%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'tenure_group_on_exit'},
                 'width': '15%',
                 'textAlign': 'left'},
            ],
            style_cell={
                'backgroundColor': '#EDEDED',
                'textOverflow': 'ellipsis',
                'font-size': '0.8rem',
            },
            style_table={
                'width': '98%',
                'maxHeight': '450px'
            },
        )
        return result_table

    @app.callback(Output('selected_dates_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_selected_dates_text(dates_range):
        start_date = dates_list[dates_range[0]-1]
        end_date = dates_list[dates_range[1]-1]
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
            return 'Все'
        return functions_list[0]

    @app.callback(
        Output('total_to_graph', 'figure'),
        [Input('lines_checklist', 'value'),
         Input('functions_dropdown', 'value'),
         Input("functions_radio", "value"),
         Input('dates_slider', 'value')])
    def get_total_to_graph(selected_lines, selected_functions, selected_radio, dates_range):

        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')

        if not isinstance(selected_lines, list):
            selected_lines = [selected_lines]
        if not isinstance(selected_functions, list):
            selected_functions = [selected_functions]
        df = pd.read_sql('''
            SELECT 
                month_start,
                headcount_average,
                event_exit,
                event_exit_voluntary,
                event_exit_involuntary,
                function,
                line
            FROM
                hc_data_main;
        ''', con=engine, parse_dates=['month_start'])
        if selected_radio == 'include':
            dff = df[df['line'].isin(selected_lines) & df['function'].isin(selected_functions)]
        elif selected_radio == 'exclude':
            dff = df[df['line'].isin(selected_lines) & ~df['function'].isin(selected_functions)]
        else:
            dff = df[df['line'].isin(selected_lines)]
        df_total = pd.pivot_table(
            dff,
            index=['month_start'],
            values=['headcount_average', 'event_exit', 'event_exit_voluntary', 'event_exit_involuntary'],
            aggfunc='sum',
            fill_value=0,
            dropna=False).reset_index()

        totals_df = df_total[(df_total['month_start'] >= start_date) &
                             (df_total['month_start'] <= end_date)].copy()
        total_avg_hc = totals_df['headcount_average'].mean()
        total_exits_vol = totals_df['event_exit_voluntary'].sum()
        total_exits_invol = totals_df['event_exit_involuntary'].sum()
        total_to = (total_exits_invol + total_exits_vol) / total_avg_hc

        title = f'Текучесть за период {datetime.strftime(start_date, "%m.%Y")} -' \
                f' {datetime.strftime(end_date, "%m.%Y")} составила {total_to:.1%}'

        df_total['turnover'] = df_total['event_exit'] / df_total['headcount_average']
        df_total['turnover_involuntary'] = df_total['event_exit_involuntary'] / df_total['headcount_average']
        df_total['turnover_voluntary'] = df_total['event_exit_voluntary'] / df_total['headcount_average']
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=df_total['month_start'],
            y=df_total['event_exit_voluntary'],
            name='Уволено Добровольно'
        ), secondary_y=False)
        fig.add_trace(go.Bar(
            x=df_total['month_start'],
            y=df_total['event_exit_involuntary'],
            name='Уволено Соглашение'
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df_total['month_start'],
            y=df_total['turnover'],
            name='Текучесть'
        ), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=df_total['month_start'],
            y=df_total['event_exit'],
            name='Всего Уволено',
            text=df_total['event_exit'],
            textposition='top center',
            mode='text'
        ), secondary_y=False)
        fig.update_layout(
            title_text=title,
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            barmode='stack',
            hovermode='x',
            legend=dict(font=dict(size=10), orientation="h"),
            dragmode="select",
        )
        fig.update_yaxes(showgrid=False, secondary_y=True, tickformat='.1%', rangemode='tozero')

        return fig

    @app.callback(
        Output('hires_attrition_graph', 'figure'),
        [Input('lines_checklist', 'value'),
         Input('functions_dropdown', 'value'),
         Input('functions_radio', 'value'),
         Input('dates_slider', 'value')])
    def get_hires_attrition_graph(selected_lines, selected_functions, selected_radio, dates_selected):
        if not isinstance(selected_lines, list):
            selected_lines = [selected_lines]
        if not isinstance(selected_functions, list):
            selected_functions = [selected_functions]
        df = pd.read_sql('''
            SELECT 
                month_start,
                event_hire,
                tenure_group_on_exit,
                function,
                line
            FROM
                hc_data_main
            WHERE
                event_hire = 1;
        ''', con=engine, parse_dates=['month_start'])
        if selected_radio == 'include':
            dff = df[df['line'].isin(selected_lines) & df['function'].isin(selected_functions)]
        elif selected_radio == 'exclude':
            dff = df[df['line'].isin(selected_lines) & ~df['function'].isin(selected_functions)]
        else:
            dff = df[df['line'].isin(selected_lines)]
        tenure_on_exit_groups = sorted(list(dff['tenure_group_on_exit'].unique()))
        try:
            tenure_on_exit_groups.remove('9: Техническое увольнение')
        except ValueError:
            pass
        dff = pd.pivot_table(
            dff,
            index=['month_start'],
            columns='tenure_group_on_exit',
            values='event_hire',
            aggfunc='sum',
            fill_value=0,
            dropna=False).reset_index()
        dff['hires_total'] = dff[tenure_on_exit_groups].sum(axis=1)
        traces = []
        for group in dff.columns:
            if group in tenure_on_exit_groups:
                color = colors_groups[group][0]
                trace = go.Bar(
                    x=dff['month_start'],
                    y=dff[group],
                    name=group[2:],
                    marker={
                        'color': color,
                    }
                )
                traces.append(trace)
        totals_trace = go.Scatter(
            x=dff['month_start'],
            y=dff['hires_total'],
            name='Всего нанято',
            text=dff['hires_total'],
            textposition='top center',
            mode='text'
        )
        traces.append(totals_trace)
        fte_graph_layout = go.Layout(
            title_text="Отток нанятых сотрудников",
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            barmode='stack',
            legend=dict(font=dict(size=10), orientation="h"),
            dragmode="select",
        )
        figure = {'data': traces, 'layout': fte_graph_layout}
        return figure

    @app.callback(
        Output('hires_attrition_pie', 'figure'),
        [Input('lines_checklist', 'value'),
         Input('functions_dropdown', 'value'),
         Input('functions_radio', 'value'),
         Input('dates_slider', 'value')])
    def get_hires_attrition_pie(selected_lines, selected_functions, selected_radio, dates_range):
        if not isinstance(selected_lines, list):
            selected_lines = [selected_lines]
        if not isinstance(selected_functions, list):
            selected_functions = [selected_functions]
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT 
                month_start,
                event_hire,
                tenure_group_on_exit,
                function,
                line
            FROM
                hc_data_main
            WHERE
                event_hire = 1;
        ''', con=engine, parse_dates=['month_start'])
        if selected_radio == 'include':
            dff = df[df['line'].isin(selected_lines) & df['function'].isin(selected_functions)]
        elif selected_radio == 'exclude':
            dff = df[df['line'].isin(selected_lines) & ~df['function'].isin(selected_functions)]
        else:
            dff = df[df['line'].isin(selected_lines)]
        dff = dff[(dff['month_start'] <= end_date) & (dff['month_start'] >= start_date)]

        dff = pd.pivot_table(
            dff,
            index='tenure_group_on_exit',
            values='event_hire',
            aggfunc='sum',
            fill_value=0,
            dropna=False).reset_index()
        dff = dff[dff['tenure_group_on_exit'] != '9: Техническое увольнение']
        total_hired = dff['event_hire'].sum()
        dff = dff.sort_values(by=['tenure_group_on_exit'])
        dff['groups'] = dff['tenure_group_on_exit'].apply(lambda x: colors_groups[x][0])

        trace = go.Pie(
            labels=dff['tenure_group_on_exit'],
            values=dff['event_hire'],
            name='Текущий статус сотрудников',
            marker={'colors': dff['groups']}
        )
        title = f'Статус {total_hired} сотрудников нанятых с {datetime.strftime(start_date, "%m.%Y")} ' \
                f'по {datetime.strftime(end_date, "%m.%Y")}'
        pie_layout = go.Layout(
            title_text=title,
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            legend=dict(font=dict(size=10), orientation="h"),
        )
        figure = {'data': [trace], 'layout': pie_layout}
        return figure

    @app.callback(Output("dates_slider", "value"),
                  [Input("total_to_graph", "selectedData"),
                   Input("hires_attrition_graph", "selectedData")],
                  [State('memory', 'data')])
    def update_year_slider_turnover(turnover_selected_points, attrition_selected_points, memory_data):
        date_range_selected = [len(dates_list) - 13, len(dates_list) - 1]
        if memory_data is None:
            return date_range_selected
        elif memory_data['last_clicked']['id'] is None:
            return date_range_selected
        elif memory_data['last_clicked']['id'] == 'turnover':
            x_points = [pd.to_datetime(point["x"], format='%Y-%m-%d') for point in turnover_selected_points["points"]]
        elif memory_data['last_clicked']['id'] == 'attrition':
            x_points = [pd.to_datetime(point["x"], format='%Y-%m-%d') for point in attrition_selected_points["points"]]
        else:
            return date_range_selected
        periods = np.unique(np.array(x_points))
        max_period = np.max(periods)
        min_period = np.min(periods)
        last_period_index = dates_list.index(max_period) + 1
        first_period_index = dates_list.index(min_period) + 1
        date_range_selected = [first_period_index, last_period_index]
        return date_range_selected

    @app.callback(Output("memory", "data"),
                  [Input("total_to_graph", "selectedData"),
                   Input("hires_attrition_graph", "selectedData")],
                  [State('memory', 'data')])
    def update_year_slider_turnover(turnover_selected_data, attrition_selected_data, current_value):

        if current_value is None:
            current_value = {
                'turnover': None,
                'attrition': None,
                'last_clicked': {
                    'id': 'n/a',
                    'value': 'nothing yet'
                }
            }
        else:
            if current_value['turnover'] != turnover_selected_data:
                current_value['last_clicked']['id'] = 'turnover'
                current_value['last_clicked']['value'] = turnover_selected_data
            elif current_value['attrition'] != attrition_selected_data:
                current_value['last_clicked']['id'] = 'attrition'
                current_value['last_clicked']['value'] = attrition_selected_data
        current_value['turnover'] = turnover_selected_data
        current_value['attrition'] = attrition_selected_data
        return current_value



    return app.server
