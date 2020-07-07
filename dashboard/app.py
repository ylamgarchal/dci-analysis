import dash
import dash_core_components as dcc
import dash_html_components as html

from dci_analysis import analyzer

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(id='container_0', children=[
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

app.title = "DCI Analysis"


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div(id='container_3', children=[
            html.Div(id='container_4', children=[
                html.Div(id='container_41', children=[
                    html.Label('Baseline Topic'),
                    dcc.Dropdown(
                        id='dropdown_topic_baseline',
                        options=[
                            {'label': 'RHEL-7.6', 'value': 'RHEL-7.6'},
                            {'label': 'RHEL-7.7', 'value': 'RHEL-7.7'},
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8.2', 'value': 'RHEL-8.2'},
                            {'label': 'RHEL-8.3', 'value': 'RHEL-8.3'},
                            {'label': 'RHEL-8.2-milestone', 'value': 'RHEL-8.2-milestone'}
                        ],
                        value='RHEL-8.0'
                   ),
                   html.Br(),
                   dcc.RadioItems(
                       id='baseline_computation',
                       options=[{'label': 'Mean', 'value': 'mean'},
                                {'label': 'Median', 'value': 'median'}],
                       value='median'
                   ),
                ]),
                html.Div(id='container_42'),
                html.Div(id='container_43', children=[
                    html.Label('Topic'),
                    dcc.Dropdown(
                        id='topic',
                        options=[
                            {'label': 'RHEL-7.6', 'value': 'RHEL-7.6'},
                            {'label': 'RHEL-7.7', 'value': 'RHEL-7.7'},
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8.2', 'value': 'RHEL-8.2'},
                            {'label': 'RHEL-8.3', 'value': 'RHEL-8.3'},
                            {'label': 'RHEL-8.2-milestone', 'value': 'RHEL-8.2-milestone'}
                        ],
                        value='RHEL-8.1'
                   ),
                   html.Br(),
                   html.Button(id='submit-button-comparison', n_clicks=0, children='Compute')
                ])
            ]),
            html.Div(id='container_5', children=[
                html.Br(),
                html.Div(id='comparison'),
                html.Br(),
                html.Div(id='trend')
            ])
        ])
    else:
        return html.Div([
            html.H3('You are on page {}'.format(pathname))
        ])




@app.callback([dash.dependencies.Output('comparison', 'children'),
              dash.dependencies.Output('trend', 'children')],
              [dash.dependencies.Input('submit-button-comparison', 'n_clicks')],
              [dash.dependencies.State('dropdown_topic_baseline', 'value'),
               dash.dependencies.State('baseline_computation', 'value'),
               dash.dependencies.State('topic', 'value')])
def update_output(n_clicks, baseline_topic, baseline_computation, topic):
    if n_clicks == 0:
        return ('Compute the overview comparison between topics !',
                'Trend of the view between topics !')
    else:
        if baseline_computation == 'median':
            compared_jobs = analyzer.comparison_with_median(baseline_topic, topic)
        else:
            compared_jobs = analyzer.comparison_with_mean(baseline_topic, topic)
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

        interval = int((max - min) / 25)
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
                    'title': 'Baseline %s/%s vs %s' % (baseline_topic, baseline_computation, topic),
                    'xaxis':{
                        'title':'Intervals of deltas (percentage), lower is better'
                    },
                    'yaxis':{
                        'title':'Number of tests'
                    },
                }
            }
        )

        trend_values = []
        for j in range(0, compared_jobs.shape[1]):
            job_column = []
            for i in range(0, compared_jobs.shape[0]):
                value = compared_jobs.iloc[i,j]
                job_column.append(value)
            job_column.sort()
            index_95th = int(len(job_column) * 0.95)
            trend_values.append(job_column[index_95th])

        trends = dcc.Graph(
            figure={
                'data': [
                    {
                        'type': 'line',
                        'x': list(compared_jobs.columns),
                        'y': trend_values
                    },
                ],
                'layout': {
                    'title': 'Evolution of the 95th tests, %s/%s vs %s' % (baseline_topic, baseline_computation, topic),
                    'xaxis':{
                        'title':'%s/Jobs' % baseline_computation
                    },
                    'yaxis':{
                        'title':'Maximum evolution of 95% tests'
                    },
                }
            }
        )

        return (comparisons, trends)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
