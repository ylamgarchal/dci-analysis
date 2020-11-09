import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime as dt
from datetime import timedelta

from dci_analysis import analyzer
import numpy

import glob
import os


dashboard = dash.Dash(__name__, suppress_callback_exceptions=True)

dashboard.layout = html.Div(id='container_0', children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='container_1', children=[
        html.H1('DCI Analysis')
    ]),
    html.Div(id='container_2', children=[
        html.Div(id="menu", children=[
            dcc.Link('Overview', href='/'),
            html.Br(),
            dcc.Link('Jobs details', href='/jobs-details')
        ]),
        html.Div(id='page-content')
        ]
    )
])

dashboard.title = "DCI Analysis"


@dashboard.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div(id='container_3', children=[
            html.Div(id='container_4', children=[
                html.Div(id='container_41', children=[
                    html.Label('Topic 1'),
                    dcc.Dropdown(
                        id='dropdown_topic_1',
                        options=[
                            {'label': 'RHEL-7.6-milestone', 'value': 'RHEL-7.6-milestone'},
                            {'label': 'RHEL-7.7-milestone', 'value': 'RHEL-7.7-milestone'},
                            {'label': 'RHEL-7.8-milestone', 'value': 'RHEL-7.8-milestone'},
                            {'label': 'RHEL-7.9-milestone', 'value': 'RHEL-7.9-milestone'},
                            {'label': 'RHEL-7.6', 'value': 'RHEL-7.6'},
                            {'label': 'RHEL-7.7', 'value': 'RHEL-7.7'},
                            {'label': 'RHEL-7.8', 'value': 'RHEL-7.8'},
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8.2', 'value': 'RHEL-8.2'},
                            {'label': 'RHEL-8.3', 'value': 'RHEL-8.3'},
                            {'label': 'RHEL-8.4', 'value': 'RHEL-8.4'},
                            {'label': 'RHEL-8.0-milestone', 'value': 'RHEL-8.0-milestone'},
                            {'label': 'RHEL-8.1-milestone', 'value': 'RHEL-8.1-milestone'},
                            {'label': 'RHEL-8.2-milestone', 'value': 'RHEL-8.2-milestone'},
                            {'label': 'RHEL-8.3-milestone', 'value': 'RHEL-8.3-milestone'}
                        ],
                        value='RHEL-8.2-milestone'
                   ),
                   html.Br(),
                   html.Label('Tags'),
                   dcc.Input(id='topic_1_tags',
                             value='x86_64'),
                   html.Br(),
                   html.Div(
                       dcc.DatePickerRange(
                           id='topic_1_timeframe'
                       )),
                   html.Br(),
                   dcc.RadioItems(
                       id='topic_1_computation',
                       options=[{'label': 'Mean', 'value': 'mean'},
                                {'label': 'Median', 'value': 'median'}],
                       value='median'
                   ),
                   html.Br(),
                   html.Label('Evolution percentage'),
                   dcc.Input(id='evolution_percentage_value',
                             value='95'),
                   html.Br(),
                ]),
                html.Div(id='container_42'),
                html.Div(id='container_43', children=[
                    html.Label('Topic 2'),
                    dcc.Dropdown(
                        id='dropdown_topic_2',
                        options=[
                            {'label': 'RHEL-7.6-milestone', 'value': 'RHEL-7.6-milestone'},
                            {'label': 'RHEL-7.7-milestone', 'value': 'RHEL-7.7-milestone'},
                            {'label': 'RHEL-7.8-milestone', 'value': 'RHEL-7.8-milestone'},
                            {'label': 'RHEL-7.9-milestone', 'value': 'RHEL-7.9-milestone'},
                            {'label': 'RHEL-7.6', 'value': 'RHEL-7.6'},
                            {'label': 'RHEL-7.7', 'value': 'RHEL-7.7'},
                            {'label': 'RHEL-7.8', 'value': 'RHEL-7.8'},
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8.2', 'value': 'RHEL-8.2'},
                            {'label': 'RHEL-8.3', 'value': 'RHEL-8.3'},
                            {'label': 'RHEL-8.4', 'value': 'RHEL-8.4'},
                            {'label': 'RHEL-8.0-milestone', 'value': 'RHEL-8.0-milestone'},
                            {'label': 'RHEL-8.1-milestone', 'value': 'RHEL-8.1-milestone'},
                            {'label': 'RHEL-8.2-milestone', 'value': 'RHEL-8.2-milestone'},
                            {'label': 'RHEL-8.3-milestone', 'value': 'RHEL-8.3-milestone'}
                        ],
                        value='RHEL-8.3-milestone'
                   ),
                   html.Br(),
                   html.Label('Tags'),
                   dcc.Input(id='topic_2_tags',
                             value='x86_64'),
                   html.Br(),
                   html.Div(
                       dcc.DatePickerRange(
                           id='topic_2_timeframe'
                       )),
                   html.Br(),
                   dcc.RadioItems(
                       id='topic_2_computation',
                       options=[{'label': 'Mean', 'value': 'mean'},
                                {'label': 'Median', 'value': 'median'},
                                {'label': 'Latest', 'value': 'latest'}],
                       value='latest'
                   ),
                   html.Br(),
                   html.Button(id='submit-button-comparison', n_clicks=0, children='Compute')
                ])
            ]),
            html.Div(id='container_5', children=[
                html.Br(),
                html.Div(id='comparison'),
                html.Br(),
                html.H3('Comparison details'),
                html.Div(id='comparison_details'),
                html.Br(),
                html.H3('Coefficient of variation topic 1'),
                html.Div(id='coeff_var_1'),
                html.Br(),
                html.H3('Coefficient of variation topic 2'),
                html.Div(id='coeff_var_2'),
                html.Br(),
                html.Div(id='trend'),
                html.Br(),
                html.H3('Topic 1/Sum graph per class'),
                html.Div(id='graph_per_class_1'),
                html.Br(),
                html.H3('Topic 2/Sum graph per class'),
                html.Div(id='graph_per_class_2')
            ])
        ])
    else:
        return html.Div([
            html.H3('You are on page {}'.format(pathname))
        ])


@dashboard.callback([dash.dependencies.Output('comparison', 'children'),
              dash.dependencies.Output('comparison_details', 'children'),
              dash.dependencies.Output('coeff_var_1', 'children'),
              dash.dependencies.Output('coeff_var_2', 'children'),
              dash.dependencies.Output('graph_per_class_1', 'children'),
              dash.dependencies.Output('graph_per_class_2', 'children'),
              dash.dependencies.Output('trend', 'children')],
              [dash.dependencies.Input('submit-button-comparison', 'n_clicks'),
               dash.dependencies.Input('topic_1_timeframe', 'start_date'),
               dash.dependencies.Input('topic_1_timeframe', 'end_date'),
               dash.dependencies.Input('topic_2_timeframe', 'start_date'),
               dash.dependencies.Input('topic_2_timeframe', 'end_date'),
               dash.dependencies.Input('topic_1_tags', 'value'),
               dash.dependencies.Input('topic_2_tags', 'value'),
               dash.dependencies.Input('evolution_percentage_value', 'value')],
              [dash.dependencies.State('dropdown_topic_1', 'value'),
               dash.dependencies.State('topic_1_computation', 'value'),
               dash.dependencies.State('dropdown_topic_2', 'value'),
               dash.dependencies.State('topic_2_computation', 'value')])
def update_output(n_clicks, topic_1_start_date, topic_1_end_date, topic_2_start_date,
                  topic_2_end_date, topic_1_tags, topic_2_tags, evolution_percentage_value, topic_1,
                  topic_1_computation, topic_2, topic_2_computation):
    if n_clicks == 0:
        return ('Compute the overview comparison between topics !',
                'Data table comparison details !',
                'Coefficent of variation table 1 !',
                'Coefficent of variation table 2 !',
                'Topic 1 / Sum Graph per class',
                'Topic 2 / Sum Graph per class',
                'Trend of the view between topics !')
    else:
        # Bar chart, histogram
        topic_1_start_date = analyzer.string_to_date(topic_1_start_date)
        topic_1_end_date = analyzer.string_to_date(topic_1_end_date) - timedelta(days=1)
        topic_2_start_date = analyzer.string_to_date(topic_2_start_date)
        topic_2_end_date = analyzer.string_to_date(topic_2_end_date) - timedelta(days=1)
        if topic_1_tags:
            topic_1_tags = topic_1_tags.split(',')
        if topic_2_tags:
            topic_2_tags = topic_2_tags.split(',')

        if topic_1_computation == 'median':
            compared_jobs = analyzer.comparison_with_median(
                topic_1,
                topic_2,
                topic_1_start_date,
                topic_1_end_date,
                topic_2_start_date,
                topic_2_end_date,
                topic_1_tags,
                topic_2_tags,
                topic_2_computation)
        else:
            compared_jobs = analyzer.comparison_with_mean(
                topic_1,
                topic_2,
                topic_1_start_date,
                topic_1_end_date,
                topic_2_start_date,
                topic_2_end_date,
                topic_1_tags,
                topic_2_tags,
                topic_2_computation)
        
        min = compared_jobs.min() - 1.0
        if isinstance(min, float):
            min = int(min)
        else:
            min = int(min.min())

        max = compared_jobs.max() + 1.0
        if isinstance(max, float):
            max = int(max)
        else:
            max = int(max.max())

        interval = int((max - min) / 25.)
        intervals = []
        for i in range(min, max, interval):
            intervals.append((i, i+interval))
        intervals.sort()
        result = {}
        for i in intervals:
            result[i] = 0
        for i in range(0, compared_jobs.shape[0]):
            for j in range(0, compared_jobs.shape[1]):
                value = compared_jobs.iloc[i,j]
                for inter in intervals:
                    if value >= inter[0] and value < inter[1]:
                        result[inter] += 1
        values = []
        for inter in intervals:
            values.append(result[inter])
    
        comparisons = dcc.Graph(
            figure={
                'data': [
                    {
                        'type': 'bar',
                        'x': ['(%s,%s)' % (i,j) for i, j in intervals],
                        'y': values
                    },
                ],
                'layout': {
                    'title': 'Baseline %s/%s vs %s/%s' % (topic_1, topic_1_computation, topic_2, topic_2_computation),
                    'xaxis':{
                        'title':'Intervals of deltas (percentage), lower is better'
                    },
                    'yaxis':{
                        'title':'Number of tests'
                    },
                }
            }
        )

        # Comparisons details data table
        # show the delta of each test case in percentage
        data_table = []
        # compared_jobs contains only one column
        job_id=compared_jobs.columns.tolist()[0]
        compared_jobs.sort_values(by=job_id, ascending=False, inplace=True)
        testcases = compared_jobs.index.tolist()
        data = []
        for testcase in testcases:
            if compared_jobs.loc[testcase, job_id] >= 15:
                data.append({'testcase': testcase,
                             'value': compared_jobs.loc[testcase, job_id]})
        comparisons_details = dash_table.DataTable(
            id='table',
            columns=[{"name": "testcase", "id": "testcase"},
                     {"name": "value", "id": "value"}],
            data=data,
            page_current=0,
            page_size=15
        )

        if topic_1_computation == 'median':
            compared_jobs = analyzer.comparison_with_median(
                topic_1,
                topic_2,
                topic_1_start_date,
                topic_1_end_date,
                topic_2_start_date,
                topic_2_end_date,
                topic_1_tags,
                topic_2_tags)
        else:
            compared_jobs = analyzer.comparison_with_mean(
                topic_1,
                topic_2,
                topic_1_start_date,
                topic_1_end_date,
                topic_2_start_date,
                topic_2_end_date,
                topic_1_tags,
                topic_2_tags)

        # Coefficient of Variation data table
        def get_coefficient_variation_table(topic_name, topic_2_start_date, topic_2_end_date, topic_tags):
            jobs = analyzer.get_jobs_dataset(topic_name, topic_2_start_date, topic_2_end_date, topic_tags)
            jobs_mean = jobs.apply(numpy.mean,axis=1)
            jobs_std = jobs.apply(numpy.std, axis=1)
            coeff_var = jobs_std / jobs_mean
            coeff_var.sort_values(ascending=False, inplace=True)

            data_table = []
            testcases = coeff_var.index.tolist()
            data = []
            for testcase in testcases:
                data.append({'testcase': testcase,
                            'value': coeff_var[testcase]})
            coefficient_variations_table = dash_table.DataTable(
                id='table',
                columns=[{"name": "testcase", "id": "testcase"},
                        {"name": "value", "id": "value"}],
                data=data,
                page_current=0,
                page_size=15
            )

            return coefficient_variations_table

        coefficient_variations_table_1 = get_coefficient_variation_table(
            topic_1, topic_1_start_date, topic_1_end_date, topic_1_tags)

        coefficient_variations_table_2 = get_coefficient_variation_table(
            topic_2, topic_2_start_date, topic_2_end_date, topic_2_tags)

        # graph per class
        def graph_per_class(topic, topic_start_date, topic_end_date, topic_tags):
            def getClass(testname):
                return testname.split('/')[0]
            jobs = analyzer.get_jobs_dataset(topic, topic_start_date, topic_end_date, topic_tags)
            testnames = jobs.index.tolist()
            classes = list(map(getClass, testnames))
            jobs['class'] = classes
            jobs_sum_per_class = jobs.groupby('class').sum()
            jobs_columns = list(jobs_sum_per_class.columns)
            jobs_index = list(jobs_sum_per_class.index)

            nb_rows = len(jobs_index)

            fig = make_subplots(
                rows=nb_rows, cols=1,
                subplot_titles=jobs_index)

            for row, j_i in enumerate(jobs_index, 1):
                j_c = list(range(len(jobs_columns)))
                fig.append_trace(go.Scatter(x=j_c, text=jobs_columns, y=list(jobs_sum_per_class.loc[j_i]), name="lol"),
                            row=row, col=1)

            fig.update_layout(height=1200, showlegend=False)
            return dcc.Graph(figure=fig)
        
        graph_per_class_topic_1 = graph_per_class(topic_1, topic_1_start_date, topic_1_end_date, topic_1_tags)
        graph_per_class_topic_2 = graph_per_class(topic_2, topic_2_start_date, topic_2_end_date, topic_2_tags)

        # Trends graph
        evolution_percentage_value
        float_evolution_percentage_value = float(evolution_percentage_value) / 100.
        trend_values = []
        for j in range(0, compared_jobs.shape[1]):
            job_column = []
            for i in range(0, compared_jobs.shape[0]):
                value = compared_jobs.iloc[i,j]
                job_column.append(value)
            job_column.sort()
            index_percentage = int(len(job_column) * float_evolution_percentage_value)
            trend_values.append(job_column[index_percentage])

        trends = dcc.Graph(
            figure={
                'data': [
                    {
                        'type': 'line',
                        'name': 'trend',
                        'x': list(compared_jobs.columns),
                        'y': trend_values
                    }
                ],
                'layout': {
                    'title': 'Evolution of the %sth tests, %s/%s vs %s/%s' % (evolution_percentage_value, topic_1, topic_1_computation, topic_2, topic_2_computation),
                    'xaxis':{
                        'title':'%s/Jobs' % topic_1_computation
                    },
                    'yaxis':{
                        'title':'Maximum evolution of 95% tests'
                    },
                }
            }
        )

        return (comparisons, comparisons_details, coefficient_variations_table_1, coefficient_variations_table_2, graph_per_class_topic_1, graph_per_class_topic_2, trends)


def get_min_max_date_from_topic(topic_name):
    csv_files = glob.glob('%s/%s/*.csv' % (analyzer.WORKING_DIR, topic_name))
    sorted_csv_files = analyzer.get_sorted_csv_files(csv_files, topic_name)
    if len(sorted_csv_files) >= 2:
        min_file = sorted_csv_files[0]
        min_date = analyzer.string_to_date(min_file.split('/')[1].split('_')[0])
        max_file = sorted_csv_files[-1]
        max_date = analyzer.string_to_date(max_file.split('/')[1].split('_')[0]) + timedelta(days=1)
        return min_date, min_date, max_date, max_date
    else:
        return None, None, None, None


@dashboard.callback([dash.dependencies.Output('topic_1_timeframe', 'min_date_allowed'),
                     dash.dependencies.Output('topic_1_timeframe', 'start_date'),
                     dash.dependencies.Output('topic_1_timeframe', 'max_date_allowed'),
                     dash.dependencies.Output('topic_1_timeframe', 'end_date')],
                    [dash.dependencies.Input('dropdown_topic_1', 'value')])
def update_topic_1_timeframe(topic_1):
    return get_min_max_date_from_topic(topic_1)


@dashboard.callback([dash.dependencies.Output('topic_2_timeframe', 'min_date_allowed'),
                     dash.dependencies.Output('topic_2_timeframe', 'start_date'),
                     dash.dependencies.Output('topic_2_timeframe', 'max_date_allowed'),
                     dash.dependencies.Output('topic_2_timeframe', 'end_date')],
                    [dash.dependencies.Input('dropdown_topic_2', 'value')])
def update_topic_2_timeframe(topic_2):
    return get_min_max_date_from_topic(topic_2)


if __name__ == '__main__':
    dashboard.run_server(host=os.getenv('DCI_ANALYSIS_HOST', '0.0.0.0'), port=os.getenv('DCI_ANALYSIS_PORT', 1234), debug=True)
