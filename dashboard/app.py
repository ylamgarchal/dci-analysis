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
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8-milestone', 'value': 'RHEL-8-milestone'}
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
                            {'label': 'RHEL-8.0', 'value': 'RHEL-8.0'},
                            {'label': 'RHEL-8.1', 'value': 'RHEL-8.1'},
                            {'label': 'RHEL-8-milestone', 'value': 'RHEL-8-milestone'}
                        ],
                        value='RHEL-8.1'
                   ),
                   html.Br(),
                   html.Button(id='submit-button-comparison', n_clicks=0, children='Compute')
                ])
            ]),
            html.Div(id='container_5', children=[
                html.Br(),
                html.Div(id='result')
            ])
        ])
    else:
        return html.Div([
            html.H3('You are on page {}'.format(pathname))
        ])




@app.callback(dash.dependencies.Output('result', 'children'),
              [dash.dependencies.Input('submit-button-comparison', 'n_clicks')],
              [dash.dependencies.State('dropdown_topic_baseline', 'value'),
               dash.dependencies.State('baseline_computation', 'value'),
               dash.dependencies.State('topic', 'value')])
def update_output(n_clicks, baseline_topic, baseline_computation, topic):
    if n_clicks == 0:
        return 'Compute the overview comparison between topics !'
    else:
        if baseline_computation == 'median':
            compared_jobs = analyzer.comparison_with_median(baseline_topic, topic)
        else:
            compared_jobs = analyzer.comparison_with_mean(baseline_topic, topic)
        min = int(compared_jobs.min().min() - 1)
        max = int(compared_jobs.max().max() + 1)
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
    
        return dcc.Graph(
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
    #else:
    #    return str(analyzer.comparison_with_median(baseline_topic, topic))

if __name__ == '__main__':
    app.run_server(debug=True)
