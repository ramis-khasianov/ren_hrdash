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

url_base = '/dash/dashfte/'

dates_list = sorted(list(
    pd.read_sql('SELECT DISTINCT month_start FROM hc_data_main',
                con=engine, parse_dates=['month_start'])['month_start'].dropna()))
dates_marks = {i: "" for i in range(len(dates_list))}
dates_slider = dcc.RangeSlider(
    id='dates_slider',
    value=[len(dates_list)-13, len(dates_list)-1],
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

layout = html.Div([
    html.Div([
        html.Div([
            html.H6(id='selected_dates_text'),
            dates_slider
        ],
            className='pretty_container six columns'),
        html.Div(
            [html.H6(id='current_fte_value'), html.P(id='current_fte_text')],
            id='current_fte_container',
            className="mini_container three columns",
        ),
        html.Div(
            [html.H6(id='change_fte_value'), html.P(id='change_fte_text')],
            id='change_fte_container',
            className="mini_container three columns",
        )],
        id="info-container",
        className="row flex_display",
    ),
    html.Div([
        dcc.Graph(id='total_fte_graph')
    ],
        className='pretty_container'),
    html.Div(
        id='fte_table_container',
        className='pretty_container'),
    html.Div([
        html.Div([
            html.Div(
                id='selected_n_functions_text',
                className="control_label"),
            n_function_show_slider,
            le_checklist
        ], className='pretty_container three columns'),
        html.Div([
            dcc.Graph(id='change_fte_wf'),
        ], className='pretty_container nine columns'),
    ], className="row flex_display"),
    html.Div([
        html.Div([
            dcc.Graph(id='function_fte_graph')
        ], className='pretty_container four columns'),
        html.Div([
            html.Div(id='detailed_function_table_container')
        ], className='pretty_container eight columns'),
    ], className="row flex_display")
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

    # Панелька с датаслайдером
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

    # Панель с текущей численностью
    @app.callback(Output('current_fte_value', 'children'),
                  [Input('dates_slider', 'value')])
    def get_current_fte_value(dates_range):
        current_date = dates_list[dates_range[1] - 1]
        period = datetime.strftime(current_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT legal_entity_group, fte
            FROM hc_data_main
            WHERE period = "{}"
        '''.format(period), con=engine)
        current_fte = round(df['fte'].sum(), 1)
        return current_fte

    @app.callback(Output('current_fte_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_current_fte_text(dates_range):
        current_date = dates_list[dates_range[1] - 1]
        period_text = "Численность на " + datetime.strftime(current_date, '%B %Y')
        return period_text

    # Панель с изменением численности в процентах
    @app.callback(Output('change_fte_value', 'children'),
                  [Input('dates_slider', 'value')])
    def get_change_fte_value(dates_range):
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df = pd.read_sql('''
                SELECT period, legal_entity_group, SUM(fte) AS fte
                FROM hc_data_main
                WHERE period = "{}" OR period = "{}"
                GROUP BY period, legal_entity_group
            '''.format(start_period, end_period), con=engine)
        start_fte = df[df['period'] == start_period]['fte'].sum()
        end_fte = df[df['period'] == end_period]['fte'].sum()
        fte_change = "{0:.1%}".format(end_fte / start_fte - 1)
        return fte_change

    @app.callback(Output('change_fte_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_change_fte_text(dates_range):
        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        text_string = 'Изменение FTE с {}'.format(
            str(datetime.strftime(start_date, '%B %Y')) +
            " по " +
            str(datetime.strftime(end_date, '%B %Y')))
        return text_string

    @app.callback(
        Output('total_fte_graph', 'figure'),
        [Input('dates_slider', 'value')])
    def get_total_fte_graph(dates_range):
        df = pd.read_sql('''
            SELECT month_start, legal_entity_group, SUM(fte) AS fte
            FROM hc_data_main
            GROUP BY month_start, legal_entity_group
        ''', con=engine, parse_dates=['month_start'])
        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        traces = []
        for le in df['legal_entity_group'].unique():
            colors = []
            for clr in dates_list:
                if start_date <= clr <= end_date:
                    colors.append(colors_le[le][0])
                else:
                    colors.append(colors_le[le][1])
            df_le = df[df['legal_entity_group'] == le]
            trace = go.Bar(
                x=df_le['month_start'],
                y=df_le['fte'],
                name=le,
                marker={
                    'color': colors,
                }
            )
            traces.append(trace)
        df_total = df.groupby('month_start').agg(fte=('fte', 'sum')).reset_index()
        totals_trace = go.Scatter(
            x=df_total['month_start'],
            y=df_total['fte'].round(0),
            name='Всего',
            text=df_total['fte'].round(0),
            textposition='top center',
            mode='text'
        )
        traces.append(totals_trace)
        fte_graph_layout = go.Layout(
            title_text="Динамика численности группы компаний",
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            barmode='stack',
            legend=dict(font=dict(size=10), orientation="h")
        )
        figure = {'data': traces, 'layout': fte_graph_layout}
        return figure

    @app.callback(
        Output('fte_table_container', 'children'),
        [Input('dates_slider', 'value')])
    def get_fte_table(dates_range):
        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        df = pd.read_sql('''
            SELECT month, year, SUM(fte) AS fte
            FROM hc_data_main
            GROUP BY year, month
        ''', con=engine)
        df['fte'] = df['fte'].round(1)
        dff = pd.pivot_table(
            df,
            index='year',
            columns='month',
            values='fte',
            aggfunc='sum',
            fill_value='-'
        ).reset_index()
        data = dff.to_dict('records')
        result_table = dash_table.DataTable(
            data=data,
            id='total_fte_table',
            style_as_list_view=True,
            columns=[
                {'name': 'Год', 'id': 'year'},
                {'name': 'Янв', 'id': '1'},
                {'name': 'Фев', 'id': '2'},
                {'name': 'Мар', 'id': '3'},
                {'name': 'Апр', 'id': '4'},
                {'name': 'Май', 'id': '5'},
                {'name': 'Июн', 'id': '6'},
                {'name': 'Июл', 'id': '7'},
                {'name': 'Авг', 'id': '8'},
                {'name': 'Сен', 'id': '9'},
                {'name': 'Окт', 'id': '10'},
                {'name': 'Ноя', 'id': '11'},
                {'name': 'Дек', 'id': '12'},
            ],
            style_cell={
                'backgroundColor': '#EDEDED',
                'textOverflow': 'ellipsis',
            }
        )
        return result_table

    @app.callback(
        Output('change_fte_wf', 'figure'),
        [Input('dates_slider', 'value'),
         Input('n_functions_show_slider', 'value'),
         Input('le_checklist', 'value')])
    def get_change_fte_wf(dates_range, n_functions_selected, le_selected):
        if not isinstance(le_selected, list):
            le_condition = '= "' + str(le_selected) + '"'
        else:
            le_condition = 'in ' + str(tuple(le_selected))
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        print(start_period, end_period)
        n_cases = n_functions_selected
        df_start = pd.read_sql('''
            SELECT month_start, SUM(fte) as fte 
            FROM hc_data_main
            WHERE period = "{}" AND legal_entity_short {}
        '''.format(start_period, le_condition), con=engine)
        df_start['title'] = 'FTE на ' + datetime.strftime(start_date, '%B %Y')
        df_start['measure'] = 'absolute'
        df_end = pd.read_sql('''
            SELECT month_start, SUM(fte) as fte 
            FROM hc_data_main
            WHERE period = "{}" AND legal_entity_short {}
        '''.format(end_period, le_condition), con=engine)
        df_end['title'] = 'FTE на ' + datetime.strftime(end_date, '%B %Y')
        df_end['measure'] = 'absolute'
        df_change = pd.read_sql('''
            SELECT function, period, SUM(fte) as fte 
            FROM hc_data_main
            WHERE (period = "{}" OR period = "{}") AND legal_entity_short {}
            GROUP BY function, period
        '''.format(start_period, end_period, le_condition), con=engine)
        df_change['function'].fillna('Не опознаны', inplace=True)
        dff = pd.pivot_table(
            df_change,
            index='function',
            columns='period',
            values='fte',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        dff.rename(columns={start_period: 'start_fte', end_period: 'end_fte'},
                   inplace=True)
        dff['change'] = dff['start_fte'] - dff['end_fte']
        dff['rank'] = dff['change'].abs().rank(method='first', ascending=False)
        '''
        dff.loc[dff['rank'] > n_cases, 'function'] = 'Другие'
        dff = dff.groupby(['function']).agg(change=('change', 'sum')).reset_index()
        '''
        dff['measure'] = 'relative'
        dff_top_n = dff[dff['rank'] <= n_cases].copy()
        dff_top_n.sort_values(by='change', ascending=False, inplace=True)
        other_change = (df_end['fte'].sum() - df_start['fte'].sum()) - dff_top_n['change'].sum()
        dff_others = pd.DataFrame({
            'title': ['Другое'],
            'fte': [other_change],
            'measure': ['relative']
        })

        df_result = pd.concat([
            df_start[['title', 'fte', 'measure']],
            dff_top_n[['function', 'change', 'measure']].rename(
                columns={'function': 'title', 'change': 'fte'}),
            dff_others,
            df_end[['title', 'fte', 'measure']],
        ]).round({'fte': 1})
        fig = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=df_result['measure'],
                x=df_result['title'],
                textposition="outside",
                text=df_result['fte'],
                y=df_result['fte']
            ))
        title_string = 'Изменение FTE по функциям с {}'.format(
            str(datetime.strftime(start_date, '%b %Y')) +
            " по " +
            str(datetime.strftime(end_date, '%b %Y')))
        fig.update_layout(
            title_text=title_string,
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            legend=dict(font=dict(size=10), orientation="h")
        )
        max_value = df_result['fte'].max()
        fig.update_yaxes(range=[0, max_value * 1.1])

        return fig

    @app.callback(
        Output('json_test', 'children'),
        [Input('change_fte_wf', 'clickData')])
    def return_json(clickData):
        return json.dumps(clickData, indent=2)

    @app.callback(
        Output('selected_n_functions_text', 'children'),
        [Input('n_functions_show_slider', 'value')])
    def get_selected_n_functions_text(n_functions_selected):
        text_string = 'Показать детализацию по {} функциям'.format(n_functions_selected)
        return text_string

    @app.callback(
        Output('function_fte_graph', 'figure'),
        [Input('change_fte_wf', 'clickData'),
         Input('dates_slider', 'value')])
    def get_functions_fte(clickData, dates_range):
        functions = list(pd.read_sql('''
            SELECT DISTINCT function
            FROM hc_data_main''', con=engine)['function'].dropna())
        try:
            function = clickData['points'][0]['x']
        except TypeError:
            function = None
        if function is None or function not in functions:
            function = random.choice(functions)
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT month_start, legal_entity_group, function, SUM(fte) AS fte
            FROM hc_data_main
            WHERE function = "{}"
            GROUP BY month_start, legal_entity_group
        '''.format(function), con=engine, parse_dates=['month_start'])
        df = df[(df['month_start'] >= start_date) & (df['month_start'] <= end_date)]
        traces = []
        for le in df['legal_entity_group'].unique():
            df_le = df[df['legal_entity_group'] == le]
            trace = go.Bar(
                x=df_le['month_start'],
                y=df_le['fte'],
                name=le,
                marker={
                    'color': colors_le[le][0],
                }
            )
            traces.append(trace)

        fte_graph_layout = go.Layout(
            title_text="Динамика FTE " + function,
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            barmode='stack',
            legend=dict(font=dict(size=10), orientation="h")
        )
        figure = {'data': traces, 'layout': fte_graph_layout}
        return figure

    @app.callback(
        Output('detailed_function_table_container', 'children'),
        [Input('change_fte_wf', 'clickData'),
         Input('dates_slider', 'value')])
    def get_functions_fte(clickData, dates_range):
        functions = list(pd.read_sql('''
                SELECT DISTINCT function
                FROM hc_data_main''', con=engine)['function'].dropna())
        try:
            function = clickData['points'][0]['x']
        except TypeError:
            function = None
        if function is None or function not in functions:
            function = random.choice(functions)
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT
                hc.period,
                hc.cost_center,
                SUM(hc.fte) AS fte,
                ccf.function_detailed
            FROM hc_data_main hc
            LEFT JOIN ref_cost_center_functions ccf
            ON hc.cost_center = ccf.cost_center
            WHERE 
                hc.function = "{}" AND
                (hc.period = "{}" OR hc.period = "{}")
            GROUP BY  hc.period, hc.cost_center, ccf.function_detailed
        '''.format(function, start_period, end_period), con=engine)
        df['fte'] = df['fte'].round(1)
        dff = pd.pivot_table(
            df,
            index='function_detailed',
            columns='period',
            values='fte',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        dff.rename(columns={start_period: 'start_period', end_period: 'end_period'},
                   inplace=True)
        dff['change'] = (dff['end_period'] - dff['start_period']).round(1)
        dff.sort_values(by=['change'], ascending=False, inplace=True)
        data = dff.to_dict('records')
        result_table = dash_table.DataTable(
            data=data,
            id='detailed_function_table',
            style_as_list_view=True,
            columns=[
                {'name': 'Функция', 'id': 'function_detailed'},
                {'name': 'Было', 'id': 'start_period'},
                {'name': 'Стало', 'id': 'end_period'},
                {'name': 'Изменение', 'id': 'change'},
            ],
            fixed_rows={'headers': True, 'data': 0},
            style_cell_conditional=[
                {'if': {'column_id': 'start_period'}, 'width': '50px'},
                {'if': {'column_id': 'end_period'}, 'width': '50px'},
                {'if': {'column_id': 'change'}, 'width': '50px'},
                {'if': {'column_id': 'function_detailed'},
                 'width': '35%',
                 'textAlign': 'left'}
            ],
            style_cell={
                'backgroundColor': '#EDEDED',
                'textOverflow': 'ellipsis',
            },
            style_table={
                'width': '98%',
                'maxHeight': '450px'
            },
        )

        return result_table

    return app.server
