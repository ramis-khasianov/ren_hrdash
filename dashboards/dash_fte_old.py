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

url_base = '/dash/dashfte/'


def input_to_list(input_value):
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
    options=functions_options,
    multi=True,
    value=functions_list[0],
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


layout = html.Div([
    html.Div([
        html.Div([
            html.Div(id='selected_dates_text', className="control_label"),
            dates_slider,
            html.Div("Отобрать по Юр. лицам", className="control_label"),
            le_radio,
            le_dropdown,
        ],
            className='pretty_container six columns'),
        html.Div(
            [create_toolip('current_fte_card', tooltip_text['current_fte_card']),
             html.H6(id='current_fte_value'),
             html.P(id='current_fte_text')],
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
])

excluded_content = html.Div([
    html.Div([
        html.Div([
            wf_type_radio,
            html.Div(
                id='selected_n_functions_text',
                className="control_label"),
            n_function_show_slider,
            functions_dropdown
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
        },
        {
            'href': '../../static/vendors/font-awesome/css/font-awesome.min.css',
            'rel': 'stylesheet'
        },
    ]
    app = Dash(server=server, url_base_pathname=url_base, external_stylesheets=external_stylesheets)
    apply_layout_with_auth(app, layout)

    @app.callback(
        Output("le_dropdown", "value"),
        [Input("le_radio", "value")]
    )
    def selection_drop(selected_radio):
        if selected_radio == "all":
            return list(le_dict.keys())
        elif selected_radio == 'active':
            return [x for x in le_dict.keys() if x not in ['bos', 'intouch']]  # todo check with olga about welbi
        elif selected_radio == 'grs_only':
            return ['grs']
        elif selected_radio == 'rz_only':
            return ['rz']
        else:
            return list(le_dict.keys())

    # Панелька с датаслайдером
    @app.callback(Output('selected_dates_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_selected_dates_text(dates_range):
        print(current_user.access_settings)
        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        text_string = 'Данные за период: {}'.format(
            str(datetime.strftime(start_date, '%b %Y')) +
            " - " +
            str(datetime.strftime(end_date, '%b %Y')))
        return text_string

    # Панель с текущей численностью
    @app.callback(Output('current_fte_value', 'children'),
                  [Input('dates_slider', 'value'),
                   Input('le_dropdown', 'value')])
    def get_current_fte_value(dates_range, selected_le):
        current_date = dates_list[dates_range[1] - 1]
        period = datetime.strftime(current_date, '%Y_%m')
        df = pd.read_sql('''
            SELECT legal_entity_short_eng, fte
            FROM hc_data_main
            WHERE period = "{}"
        '''.format(period), con=engine)
        dff = df[df['legal_entity_short_eng'].isin(input_to_list(selected_le))]
        current_fte = round(dff['fte'].sum(), 1)
        return current_fte

    # Текст в панельке с текущей численностью (какой месяц)
    @app.callback(Output('current_fte_text', 'children'),
                  [Input('dates_slider', 'value')])
    def get_current_fte_text(dates_range):
        current_date = dates_list[dates_range[1] - 1]
        period_text = "Численность на " + datetime.strftime(current_date, '%B %Y')
        return period_text

    # Панель с изменением численности в процентах (значение)
    @app.callback(Output('change_fte_value', 'children'),
                  [Input('dates_slider', 'value'),
                   Input('le_dropdown', 'value')])
    def get_change_fte_value(dates_range, selected_le):
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df = pd.read_sql('''
                SELECT period, legal_entity_short_eng, SUM(fte) AS fte
                FROM hc_data_main
                WHERE period = "{}" OR period = "{}"
                GROUP BY period, legal_entity_short_eng
            '''.format(start_period, end_period), con=engine)
        df = df[df['legal_entity_short_eng'].isin(input_to_list(selected_le))]
        start_fte = df[df['period'] == start_period]['fte'].sum()
        end_fte = df[df['period'] == end_period]['fte'].sum()
        fte_change_percent = "{0:+.1%}".format(end_fte / start_fte - 1)
        fte_change_absolute = "{0:+}".format(round(end_fte - start_fte, 1))
        fte_change = "{} ({} FTE)".format(fte_change_percent, fte_change_absolute)
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
        [Input('dates_slider', 'value'),
         Input('le_dropdown', 'value')])
    def get_total_fte_graph(dates_range, selected_le):
        df = pd.read_sql('''
            SELECT month_start, legal_entity_short_eng, legal_entity_group, SUM(fte) AS fte
            FROM hc_data_main
            GROUP BY month_start, legal_entity_group, legal_entity_short_eng
        ''', con=engine, parse_dates=['month_start'])
        df = df[df['legal_entity_short_eng'].isin(input_to_list(selected_le))]
        df = df.groupby(['month_start', 'legal_entity_group']).agg(
            fte=('fte', 'sum')
        ).reset_index()

        start_date = dates_list[dates_range[0] - 1]
        end_date = dates_list[dates_range[1] - 1]
        traces = []
        if 'ГРС' in df['legal_entity_group'].unique():
            le_for_graph = ['ГРС'] + [le for le in df['legal_entity_group'].unique() if le != 'ГРС']
        else:
            le_for_graph = df['legal_entity_group'].unique()
        for le in le_for_graph:
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
                },
                hovertemplate='<span style="color: #000000">' + le + ': %{y:,.0f}</span><extra></extra>',
            )
            traces.append(trace)
        df_total = df.groupby('month_start').agg(fte=('fte', 'sum')).reset_index()
        totals_trace = go.Scatter(
            x=df_total['month_start'],
            y=df_total['fte'].round(0),
            name='Всего',
            text=df_total['fte'].round(0),
            textposition='top center',
            mode='text',
            hoverinfo='skip',
            hovertemplate='<span style="background-color: #000000">Всего: %{y:,.0f}</span><extra></extra>'
        )
        traces.append(totals_trace)
        xaxis_range = [dates_list[-36] + timedelta(days=15),
                       dates_list[-1] + timedelta(days=15)]
        fte_graph_layout = go.Layout(
            title_text="Динамика FTE группы компаний",
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED",
            hovermode='x',
            barmode='stack',
            legend=dict(font=dict(size=10), orientation="h"),
            xaxis=dict(range=xaxis_range, tickformat='%m.%Y', nticks=12),

        )
        figure = {'data': traces, 'layout': fte_graph_layout}
        return figure

    @app.callback(
        Output('fte_table_container', 'children'),
        [Input('dates_slider', 'value')])
    def get_fte_table(dates_range):
        periods = dates_list[dates_range[0]:dates_range[1]]
        df = pd.read_sql('''
            SELECT month, year, SUM(fte) AS fte
            FROM hc_data_main
            GROUP BY year, month
        ''', con=engine)
        df['fte'] = df['fte'].round(1)
        df['month'] = df['month'].astype('int')
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
         Input('wf_type_radio', 'value'),
         Input('n_functions_show_slider', 'value'),
         Input('functions_dropdown', 'value'),
         Input('le_dropdown', 'value')])
    def get_change_fte_wf(dates_range, wf_type, n_functions_selected, functions_selected, le_selected):
        if not isinstance(le_selected, list):
            le_selected = [le_selected]
        if not isinstance(functions_selected, list):
            functions_selected = [functions_selected]
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        n_cases = n_functions_selected
        df_periods_total = pd.read_sql('''
            SELECT period, legal_entity_short_eng, function, SUM(fte) as fte 
            FROM hc_data_main
            WHERE period = "{}" OR period = "{}" 
            GROUP BY month_start, legal_entity_short_eng, function
        '''.format(start_period, end_period), con=engine)
        df_start = df_periods_total[df_periods_total['legal_entity_short_eng'].isin(le_selected) &
                                    (df_periods_total['period'] == start_period)]
        df_start = df_start.groupby('period').agg(fte=('fte', 'sum')).reset_index()
        df_start['title'] = 'FTE на ' + datetime.strftime(start_date, '%B %Y')
        df_start['measure'] = 'absolute'
        df_end = df_periods_total[df_periods_total['legal_entity_short_eng'].isin(le_selected) &
                                    (df_periods_total['period'] == end_period)]
        df_end = df_end.groupby('period').agg(fte=('fte', 'sum')).reset_index()
        df_end['title'] = 'FTE на ' + datetime.strftime(end_date, '%B %Y')
        df_end['measure'] = 'absolute'

        df_change = df_periods_total[df_periods_total['legal_entity_short_eng'].isin(le_selected)].copy()
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
        dff['change'] = dff['end_fte'] - dff['start_fte']
        dff['rank'] = dff['change'].abs().rank(method='first', ascending=False)
        if wf_type == 'top_n':
            dff.loc[dff['rank'] > n_cases, 'function'] = 'Другие'
        else:
            dff.loc[~dff['function'].isin(functions_selected), 'function'] = 'Другие'

        dff = dff.groupby(['function']).agg(change=('change', 'sum')).reset_index()
        dff['measure'] = 'relative'
        dff.sort_values(by='change', ascending=False, inplace=True)
        dff.loc[dff['function'] == 'Другие', 'sorter'] = 1
        dff.loc[dff['function'] != 'Другие', 'sorter'] = 0
        dff.sort_values(by='sorter', ascending=True, inplace=True)
        dff.rename(columns={'function': 'title', 'change': 'fte'}, inplace=True)
        df_result = pd.concat([
            df_start[['title', 'fte', 'measure']],
            dff[['title', 'fte', 'measure']],
            df_end[['title', 'fte', 'measure']],
        ]).round({'fte': 1})
        fig = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=df_result['measure'],
                x=df_result['title'],
                textposition="outside",
                text=df_result['fte'],
                y=df_result['fte'],
                hovertemplate='<span style="color: #000000">%{x}: %{text}</span><extra></extra>',
                decreasing={"marker": {"color": 'rgba(211, 94, 96, 1)'}},
                increasing={"marker": {"color": 'rgba(135, 186, 91, 1)'}},
                totals={"marker": {"color": 'rgba(114, 147, 203, 1)'}}
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
        [Input('employee_changes_sankey', 'clickData')])
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
    def get_detailed_functions_table(clickData, dates_range):
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

    """
    @app.callback(
        Output('employee_changes_sankey', 'figure'),
        [Input('dates_slider', 'value'),
         Input('functions_dropdown', 'value'),
         Input('le_dropdown', 'value')])
    def get_employee_sankey(dates_range, functions_selected, le_selected):
        if not isinstance(le_selected, list):
            le_selected = [le_selected]
        if not isinstance(functions_selected, list):
            functions_selected = [functions_selected]
        start_date = dates_list[dates_range[0] - 1]
        start_period = datetime.strftime(start_date, '%Y_%m')
        end_date = dates_list[dates_range[1] - 1]
        end_period = datetime.strftime(end_date, '%Y_%m')
        df_relevant_employees = pd.read_sql(
            '''
            SELECT
                id_name_birth_date,
                function,
                legal_entity_short_eng,
                first_hire_date, 
                last_exit_date
            FROM
                hc_data_main
            ''',
            parse_dates=['first_hire_date', 'last_exit_date'],
            con=engine)
        df_first_period = pd.read_sql(
            '''
            SELECT DISTINCT
                id_name_birth_date,
                person_fte_dict,
                legal_entities_active,
                legal_entities_present,
                main_le,
                person_fte_total
            FROM
                hc_data_main
            WHERE
                period = "{}"
            '''.format(start_period),
            con=engine)
        df_second_period = pd.read_sql(
            '''
            SELECT DISTINCT
                id_name_birth_date,
                person_fte_dict,
                legal_entities_active,
                legal_entities_present,
                main_le,
                person_fte_total
            FROM
                hc_data_main
            WHERE
                period = "{}"
            '''.format(end_period),
            con=engine)
        df_relevant_employees = df_relevant_employees[
            (df_relevant_employees['legal_entity_short_eng'].isin(le_selected)) &
            (df_relevant_employees['function'].isin(functions_selected))
        ]

        df_relevant_employees = df_relevant_employees[[
            'id_name_birth_date', 'first_hire_date', 'last_exit_date']
        ].drop_duplicates()

        df_first_period.columns = ['first_' + col if
            col != 'id_name_birth_date' else col for col in df_first_period.columns]
        df_second_period.columns = ['second_' + col if
            col != 'id_name_birth_date' else col for col in df_second_period.columns]

        df = df_relevant_employees.merge(
            df_first_period, how='left', on='id_name_birth_date'
        ).merge(
            df_second_period, how='left', on='id_name_birth_date')

        df['first_person_fte_total'].fillna(0, inplace=True)
        df['second_person_fte_total'].fillna(0, inplace=True)
        df['second_person_fte_total'].sum()

        df.loc[(df['first_person_fte_dict'] == df['second_person_fte_dict']) &
               (df['first_legal_entities_active'] == df['second_legal_entities_active']) &
               (df['first_legal_entities_present'] == df['second_legal_entities_present']) &
               (df['first_main_le'] == df['second_main_le']) &
               (df['first_person_fte_total'] == df['second_person_fte_total']),
               'type'] = 'same'
        df.loc[(df['last_exit_date'] <= (end_date + pd.tseries.offsets.MonthEnd(1))) &
               (df['first_person_fte_total'] > df['second_person_fte_total']),
               'type'] = 'from le to outside'

        def get_fte_dict_value(dict_string, legal_entities):
            if not isinstance(legal_entities, list):
                legal_entities = [legal_entities]
            total_fte = 0
            for le in legal_entities:
                parsed_dict = json.loads(dict_string)
                total_fte = total_fte + parsed_dict[le]
            return total_fte

        # df['start_fte_for_le'] = df['start_person_fte_dict'].apply(lambda x: get_fte_dict_value(x, ))

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Были на 01.2017", # 0
                       "Пришли из вне", # 1
                       "Ушли вовне", # 2
                       "Остались на 11.2019 без изменений", # 3
                       "Были в других ЮЛ на 01.2017", # 4
                       "Ушли в другие ЮЛ"], # 5
                color="blue"
            ),
            link=dict(
                source=[0, 0, 0, 1, 1, 4],  # indices correspond to labels, eg A1, A2, A2, B1, ...
                target=[3, 2, 5, 2, 3, 3],
                value=[4, 3, 2, 3, 4, 8]
            ))])

        fig.update_layout(
            title_text="Изменение численности",
            font_size=10,
            autosize=True,
            margin=dict(l=30, r=30, b=20, t=40),
            plot_bgcolor="#EDEDED",
            paper_bgcolor="#EDEDED"
        )

        return fig
        
        """

    return app.server
