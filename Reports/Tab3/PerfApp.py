import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import flask
import re
import os
from dash.dependencies import Output, State, Input
import dash_core_components as dcc



import db_details as dd
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

from support import get_DB_details, get_Data
### ======================================================
# global declarations

external_stylesheets = [dbc.themes.COSMO]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Performance report"
server = app.server

### ======================================================

@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'), 'favicon.ico')

toast = html.Div(
    [
        dbc.Toast(
            "Please verify and enter correct build number. Data is not there for this build number.",
            id="positioned-toast",
            header="Wrong build number",
            is_open=False,
            dismissable=True,
            icon="danger",
            duration=6000,
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 25, "right": 10, "width": 350},
        ),
    ]
)

search_bar = dbc.Row(
    [
        
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url(
                        "seagate.png"), height="100px")),
                    dbc.Col(dbc.NavbarBrand(
                        "Performance Report",
                        className="ml-2", 
                        style={'font-size': 40,}), align = 'center',
                            style={'margin-left' : 180})
                            
                    ],
                    align="center",
                    no_gutters=True,
                    ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)


### =====================================================

build_options = [
            {'label' : build, 'value' : build} for build in dd.get_chain('beta')
        ]

versions = [
        {'label' : 'Beta', 'value' : 'beta'},
        {'label' : 'Release', 'value' : 'release'},
        {'label' : 'Dev', 'value' : 'dev', 'disabled': True}
]

lists = [
    {'label': 'New York City', 'value': 'NYC'},
    {'label': 'Montreal', 'value': 'MTL'},
    {'label': 'San Francisco', 'value': 'SF'}
]

statistics = [
    {'label': 'Throughput', 'value':'Throughput'},
    {'label': 'Latency', 'value':'Latency'},
    {'label': 'IOPS', 'value':'IOPS'},
    {'label': 'TTFB', 'value':'TTFB'},
    {'label': 'All', 'value':'All'},
]

tab3_content = dbc.Card(
    dbc.CardBody(
        [ 
        dbc.Row(#dbc.Col(
            [
                dcc.Dropdown(
                    id = "Version_Dropdown",
                    options = versions,
                    placeholder="select version",
                    style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "15px"}, #,'align-items': 'center', 'justify-content': 'center'
                ),

                dcc.Dropdown(
                    id = 'Build1_Dropdown',
                    placeholder="select 1st build",
                    style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "15px"}, #,'align-items': 'center', 'justify-content': 'center'
                ),
            
                dcc.Dropdown(
                    id = 'Build2_Dropdown',
                    placeholder="Select 2nd build",
                    style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "20px"}, #
                ),

                dcc.Dropdown(
                    id = "Statistics_Dropdown",
                    options = statistics,
                    placeholder="Choose filter",
                    style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "15px"}, #,'align-items': 'center', 'justify-content': 'center'
                ),
                dbc.Button("Get!", id="get_graph_button", color="success",style={'height': '35px'}),

                dcc.Graph(id='plot_Throughput'),
                dcc.Graph(id='plot_Latency'),
                dcc.Graph(id='plot_IOPS'),
                dcc.Graph(id='plot_TTFB'),
                dcc.Graph(id='plot'),
            ],#width=200),
            justify='center')
        ]
    ))
### =====================================================

tabs = dbc.Tabs(
    [
        dbc.Tab(tab3_content, label="Engineers Report", style={
                'margin-left': 20, 'margin-right': 20}),

        
    ],
    className="nav nav nav-pills nav-fill nav-pills flex-column flex-sm-row",
    style={'margin-left': 20, 'margin-right': 20, 'margin-top' : 20} #, 'color' : "#6ebe4a"
)


### =====================================================

app.layout = html.Div([
    navbar,
    tabs,
    html.Div(id='dd-output-container'),
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    toast,
    html.Link(
        rel='stylesheet',
        href='/static/topography.css'
    )]) 

### =====================================================
# call back for eng report aka first tab

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Output('Build1_Dropdown', 'options'),
    dash.dependencies.Output('Build2_Dropdown', 'options'),],
    [dash.dependencies.Input('Version_Dropdown', 'value')],
)
def versionCallback(value):
    if not value:
        raise PreventUpdate
    if value == 'beta':
        return [build_options, build_options]
    elif value == 'release':
        return [lists, lists]

    return [None, None]

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Output('plot', 'figure'),
    [dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),]
    #dash.dependencies.Input('Statistics_Dropdown', 'value')],
)
def update_graph1(build1, build2):
    objects = ['4Kb','100Kb','1Mb','5Mb','36Mb','64Mb','128Mb','256Mb']
    if not (build1 and build2):
        raise PreventUpdate
    
    from support import get_all_traces
    return get_all_traces(build1, build2, objects)

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Output('plot_Throughput', 'figure'),
    [dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value')],
    #dash.dependencies.Input('Statistics_Dropdown', 'value')],
)
def update_graph2(build1, build2):
    objects = ['4Kb','100Kb','1Mb','5Mb','36Mb','64Mb','128Mb','256Mb']
    param = 'Throughput'
    if not (build1 and build2):
        raise PreventUpdate
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []

    data_read_B1 = get_Data(build1,'Read',param)    
    data_write_B1 = get_Data(build1,'Write',param)
    data_read_B2 = get_Data(build2,'Read',param)
    data_write_B2 = get_Data(build2,'Write',param)


    trace1 = go.Scatter(
        name = 'Read {} - {}'.format(param, build1),
        x = objects,
        y= data_read_B1,
        # hovermode='x',
        # hovertemplate = '%{y, MBps}<extra></extra>'
    )

    trace2 = go.Scatter(
        name = 'Write {} - {}'.format(param, build1),
        x = objects,
        y= data_write_B1,
        # hovermode='x',
        # hovertemplate = '%{y, MBps}<extra></extra>'
        
    )

    trace3 = go.Scatter(
        name = 'Read {} - {}'.format(param, build2),
        x = objects,
        y=  data_read_B2,
        # hovermode='x',
        # hovertemplate = '%{y, MBps}<extra></extra>'
        
    )

    trace4 = go.Scatter(
        name = 'Write {} - {}'.format(param, build2),
        x = objects,
        y= data_write_B2,
        # hovermode='x',
        # hovertemplate = '%{y, MBps}<extra></extra>'
    )

    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{} Variance'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (MBps)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text="Object Sizes",
            titlefont=dict(size=16)
        ),

        
    )
    return fig

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Output('plot_Latency', 'figure'),
    [dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value')],
    #dash.dependencies.Input('Statistics_Dropdown', 'value')],
)
def update_graph3(build1, build2):
    objects = ['4Kb','100Kb','1Mb','5Mb','36Mb','64Mb','128Mb','256Mb']
    param = 'Latency'
    if not (build1 and build2):
        raise PreventUpdate
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []

    data_read_B1 = get_Data(build1,'Read',param,'Avg')    
    data_write_B1 = get_Data(build1,'Write',param,'Avg')
    data_read_B2 = get_Data(build2,'Read',param,'Avg')
    data_write_B2 = get_Data(build2,'Write',param,'Avg')

    trace1 = go.Scatter(
        name = 'Read {} - {}'.format(param, build1),
        x = objects,
        y= data_read_B1
    )

    trace2 = go.Scatter(
        name = 'Write {} - {}'.format(param, build1),
        x = objects,
        y= data_write_B1,
        
    )

    trace3 = go.Scatter(
        name = 'Read {} - {}'.format(param, build2),
        x = objects,
        y=  data_read_B2,
        
    )

    trace4 = go.Scatter(
        name = 'Write {} - {}'.format(param, build2),
        x = objects,
        y= data_write_B2,
    )

    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{} Variance'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (ms)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text="Object Sizes",
            titlefont=dict(size=16)
        )
    )
    return fig

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Output('plot_IOPS', 'figure'),
    [dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value')],
    #dash.dependencies.Input('Statistics_Dropdown', 'value')],
)
def update_graph4(build1, build2):
    objects = ['4Kb','100Kb','1Mb','5Mb','36Mb','64Mb','128Mb','256Mb']
    if not (build1 and build2):
        raise PreventUpdate
    param = 'IOPS'
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []
  
    data_read_B1 = get_Data(build1,'Read',param)    
    data_write_B1 = get_Data(build1,'Write',param)
    data_read_B2 = get_Data(build2,'Read',param)
    data_write_B2 = get_Data(build2,'Write',param)

    trace1 = go.Scatter(
        name = 'Read {} - {}'.format(param, build1),
        x = objects,
        y= data_read_B1
    )

    trace2 = go.Scatter(
        name = 'Write {} - {}'.format(param, build1),
        x = objects,
        y= data_write_B1,
        
    )

    trace3 = go.Scatter(
        name = 'Read {} - {}'.format(param, build2),
        x = objects,
        y=  data_read_B2,
        
    )

    trace4 = go.Scatter(
        name = 'Write {} - {}'.format(param, build2),
        x = objects,
        y= data_write_B2,
    )

    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{} Variance'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text="Object Sizes",
            titlefont=dict(size=16)
        )
    )
    return fig

@app.callback(
    #dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Output('plot_TTFB', 'figure'),
    [dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value')],
    #dash.dependencies.Input('Statistics_Dropdown', 'value')],
)
def update_graph5(build1, build2):
    objects = ['4Kb','100Kb','1Mb','5Mb','36Mb','64Mb','128Mb','256Mb']
    param = 'TTFB'
    if not (build1 and build2):
        raise PreventUpdate
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []

    data_read_B1 = get_Data(build1,'Read',param,'Avg')    
    data_write_B1 = get_Data(build1,'Write',param,'Avg')
    data_read_B2 = get_Data(build2,'Read',param,'Avg')
    data_write_B2 = get_Data(build2,'Write',param,'Avg')

    trace1 = go.Scatter(
        name = 'Read {} - {}'.format(param, build1),
        x = objects,
        y= data_read_B1
    )

    trace2 = go.Scatter(
        name = 'Write {} - {}'.format(param, build1),
        x = objects,
        y= data_write_B1,
        
    )

    trace3 = go.Scatter(
        name = 'Read {} - {}'.format(param, build2),
        x = objects,
        y=  data_read_B2,
        
    )

    trace4 = go.Scatter(
        name = 'Write {} - {}'.format(param, build2),
        x = objects,
        y= data_write_B2,
    )

    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{} Variance'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (ms)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text="Object Sizes",
            titlefont=dict(size=16)
        )
    )
    return fig


### =====================================================
# app configuration ends
### =====================================================
# run server 


if __name__ == '__main__':
    # run localhost:5002
    app.run_server(host='0.0.0.0', port=8008, threaded=True, debug=True)
