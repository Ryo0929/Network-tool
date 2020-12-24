import json
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table
from demos import dash_reusable_components as drc
import pandas
import sys
import base64
import datetime
import io
from dash.dependencies import Input, Output, State

cyto.load_extra_layouts()

import flask
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

#app = dash.Dash(__name__)
#server = app.server

####################### DATA INPUT AND DEFALUT SETTING  ######################

df_edge = None
df_node = None
df_color = pandas.DataFrame({'empty': []})

default_node_threshold = 1
default_edge_threshold = 1

max_node_size = "50"
min_node_size = "5"

actual_max_node_size = str(10)
actual_min_node_size = str(1)

default_connected_line_color = '#0074D9'
font_size = '20px'


####################### DATA INPUT  ######################
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    global df_edge
    global df_node
    global default_node_threshold
    global default_edge_threshold
    global actual_max_node_size
    global actual_min_node_size
    global df_color
    df_color = pandas.DataFrame({'empty': []})
    decoded = base64.b64decode(content_string)
    try:
        # Assume that the user uploaded an excel file
        df_edge = pandas.read_excel(io.BytesIO(decoded),
                                    sheet_name='edge_count')
        df_node = pandas.read_excel(io.BytesIO(decoded),
                                    sheet_name='node_count')
        default_node_threshold = df_node.head(200).iloc[[-1
                                                         ]]["count"].values[0]
        default_edge_threshold = df_edge.head(200).iloc[[-1
                                                         ]]["count"].values[0]
        actual_max_node_size = str(df_node["count"].max())
        actual_min_node_size = str(df_node["count"].min())

        #update_filter(5454)
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return get_elements(int(default_node_threshold),
                        int(default_edge_threshold))


def update_color_sheet(contents):
    print("get in update color function")
    content_type, content_string = contents.split(',')
    global df_color
    decoded = base64.b64decode(content_string)
    try:
        # Assume that the user uploaded an excel file
        df_color = pandas.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return get_elements(default_node_threshold, default_edge_threshold)


def find_color_code_from_list(word):
    # check if word is in color_list and return first row of the founded column
    index_object = df_color.columns[df_color.isin([word]).any()]
    if not index_object.empty:
        #return the color code without '#' because we can not named classes with '#'
        return index_object[0][1:7]
    else:
        return ""


def get_elements(node_threshold=default_node_threshold,
                 edge_threshold=default_edge_threshold):
    df_node_trim = df_node[df_node["count"] >= node_threshold]
    df_edge_trim = df_edge[df_edge["count"] >= edge_threshold]

    cy_edges = []
    cy_nodes = []
    nodes = set()
    for index, row in df_edge_trim.iterrows():
        source, target = row["from"], row["to"]
        if source in set(df_node_trim["tag"]) and target in set(
                df_node_trim["tag"]):
            if source not in nodes:
                nodes.add(source)
                color_code = find_color_code_from_list(source)
                node_size = df_node_trim.set_index("tag").loc[source][
                    "count"]  #set count value as node size
                cy_nodes.append({
                    "data": {
                        "id": source,
                        "label": source,
                        "size": node_size
                    },
                    "classes": color_code
                })  #use color code as class name

            if target not in nodes:
                nodes.add(target)
                color_code = find_color_code_from_list(target)
                node_size = df_node_trim.set_index("tag").loc[source]["count"]
                cy_nodes.append({
                    "data": {
                        "id": target,
                        "label": target,
                        "size": node_size
                    },
                    "classes": color_code
                })

            cy_edges.append({'data': {'source': source, 'target': target}})
    result = cy_edges + cy_nodes
    return result


def get_color_stylesheet():
    color_stylesheet = []
    for color in list(df_color.columns):
        color_stylesheet.append(
            {
                "selector": ('.' + color[1:7]),
                'style': {
                    "background-color": (color[:7])
                }
            }, )
    return color_stylesheet


def get_default_stylesheet():
    default_stylesheet = [
        {
            "selector": 'node',
            'style': {
                "width":
                "mapData(size, " + actual_min_node_size + "," +
                actual_max_node_size + "," + min_node_size + "," +
                max_node_size + ")",
                "height":
                "mapData(size, " + actual_min_node_size + "," +
                actual_max_node_size + "," + min_node_size + "," +
                max_node_size + ")",
                "color":
                "black",  #font color
                "background-color":
                "#0074D9",  #node color
                "opacity":
                0.8,
                'content':
                'data(label)',
                'font-size':
                font_size
            }
        },
        {
            "selector": 'edge',
            'style': {
                "color": "lightgrey",
                "curve-style": "bezier",
                "opacity": 0.65
            }
        },
    ]
    default_stylesheet.extend(get_color_stylesheet())
    return default_stylesheet


styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {
        'height': 'calc(98vh - 105px)'
    }
}

app.layout = html.Div([
    html.Div(
        className='eight columns',
        children=[
            dcc.Loading(
                id="loading-2",
                children=[
                    html.Div([
                        cyto.Cytoscape(
                            id='cytoscape',
                            #elements=get_elements(),
                            elements=[],
                            style={
                                'content': 'data(label)',
                                'height': '95vh',
                                'width': '100%'
                            })
                    ])
                ],
                type="circle",
            )
        ]),
    html.Div(
        className='four columns',
        children=[
            dcc.Tabs(
                id='tabs',
                children=[
                    dcc.Tab(
                        label='Control Panel',
                        children=[
                            dcc.Upload(
                                id='upload-element-data',
                                children=html.Div([
                                    'Upload element data ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                # Allow multiple files to be uploaded
                                #multiple=False
                            ),
                            html.Div(id='output-data-upload'),
                            dcc.Upload(
                                id='upload-color-data',
                                children=html.Div([
                                    'Upload color data ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                # Allow multiple files to be uploaded
                                #multiple=False
                            ),
                            #html.Div(id='output-data-upload'),
                            drc.NamedDropdown(name='Layout',
                                              id='dropdown-layout',
                                              options=drc.DropdownOptionsList(
                                                  'random', 'grid', 'circle',
                                                  'concentric', 'breadthfirst',
                                                  'cose', 'cose-bilkent',
                                                  'cola', 'euler', 'spread',
                                                  'dagre', 'klay'),
                                              value='cola',
                                              clearable=False),
                            drc.NamedInput(
                                name='Connected line Color',
                                id='input-follower-color',
                                type='text',
                                debounce=True,
                                value=default_connected_line_color,
                            ),
                            html.Div(id='current-node-threshold'),
                            drc.NamedInput(
                                name='node_filter',
                                id='node-filter-number',
                                type='number',
                                min=1,
                                debounce=True,
                                #value=default_node_threshold,
                            ),
                            html.Div(id='current-edge-threshold'),
                            drc.NamedInput(
                                name='edge_filter',
                                id='edge-filter-number',
                                type='number',
                                min=1,
                                debounce=True,
                                #value=default_edge_threshold,
                            ),
                            drc.NamedInput(
                                name='node_max_size',
                                id='node-max-size',
                                type='number',
                                min=1,
                                value=int(max_node_size),
                            ),
                            drc.NamedInput(
                                name='node_min_size',
                                id='node-min-size',
                                type='number',
                                min=1,
                                value=int(min_node_size),
                            ),
                            drc.Button(name='unfocus button',
                                       id='unfocus_button'),
                            drc.NamedInput(
                                name='font size',
                                id='font-size',
                                type='number',
                                min=1,
                                value=int(font_size[:-2]),
                            ),
                        ]),
                    dcc.Tab(
                        label='Data Table',
                        children=[
                            html.Div(style=styles['tab'],
                                     children=[
                                         html.P('Node Table:'),
                                         html.Pre(id='tap-node-json-output'),
                                         html.Hr(),
                                         html.P('Edge Table:'),
                                         html.Pre(id='tap-edge-json-output')
                                     ])
                        ])
                ]),
        ])
])


@app.callback(Output('current-node-threshold', 'children'),
              [Input('cytoscape', 'elements')])
def update_current_node_threshold(data):
    return "current node threshold:" + str(default_node_threshold)


@app.callback(Output('current-edge-threshold', 'children'),
              [Input('cytoscape', 'elements')])
def update_current_edge_threshold(data):
    return "current edge threshold:" + str(default_edge_threshold)


@app.callback(Output('tap-node-json-output', 'children'),
              [Input('cytoscape', 'elements')])
def display_tap_node(data):
    df = df_node
    if df is not None:
        child = html.Div([
            dash_table.DataTable(data=df.to_dict('records'),
                                 columns=[{
                                     'name': i,
                                     'id': i
                                 } for i in df.columns],
                                 page_size=50)
        ])
        return child


@app.callback(Output('tap-edge-json-output', 'children'),
              [Input('cytoscape', 'elements')])
def display_tap_edge(data):
    df = df_edge
    if df is not None:
	    child = html.Div([
	        dash_table.DataTable(data=df.to_dict('records'),
	                             columns=[{
	                                 'name': i,
	                                 'id': i
	                             } for i in df.columns],
	                             page_size=50)
	    ])
	    return child


@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}


@app.callback(Output('cytoscape', 'elements'), [
    Input('edge-filter-number', 'value'),
    Input('node-filter-number', 'value'),
    Input('upload-element-data', 'contents'),
    Input('upload-color-data', 'contents')
])
def update_elements(edge_number, node_number, element_contents,
                    color_contents):
    global default_edge_threshold
    global default_node_threshold
    edge_number = default_edge_threshold if edge_number is None else edge_number
    node_number = default_node_threshold if node_number is None else node_number
    ctx = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    print(ctx)
    if ctx == "upload-element-data" and element_contents is not None:
        return parse_contents(element_contents)
    if ctx == "upload-color-data" and color_contents is not None:
        return update_color_sheet(color_contents)
    if ctx in ["edge-filter-number", "node-filter-number"]:
        default_edge_threshold = int(edge_number)
        default_node_threshold = int(node_number)
        return get_elements(int(node_number), int(edge_number))
    return []


@app.callback(Output('cytoscape', 'stylesheet'), [
    Input('cytoscape', 'tapNode'),
    Input('input-follower-color', 'value'),
    dash.dependencies.Input('unfocus_button', 'n_clicks'),
    Input('node-max-size', 'value'),
    Input('node-min-size', 'value'),
    Input('font-size', 'value'),
    Input('cytoscape', 'elements')
])
def generate_stylesheet(node, follower_color, btn_clicks, max_size, min_size,
                        text_size, test):
    ctx = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    print(ctx)
    global max_node_size
    max_node_size = str(max_size)
    global min_node_size
    min_node_size = str(min_size)
    global font_size
    font_size = str(text_size) + 'px'
    if not node:
        return get_default_stylesheet()
    if ctx in [
            'unfocus_button', 'node-max-size', 'node-min-size', 'font-size'
    ]:
        return get_default_stylesheet()
    focus_stylesheet = [{
        "selector": 'node',
        'style': {
            "width":
            "mapData(size, " + actual_min_node_size + "," +
            actual_max_node_size + "," + min_node_size + "," + max_node_size +
            ")",
            "height":
            "mapData(size, " + actual_min_node_size + "," +
            actual_max_node_size + "," + min_node_size + "," + max_node_size +
            ")",
            'content':
            'data(label)',
            'opacity':
            0.2,
            'shape':
            "ellipse",
            'font-size':
            font_size
        }
    }, {
        'selector': 'edge',
        'style': {
            'opacity': 0.3,
            "curve-style": "bezier",
        }
    }, {
        "selector":
        'node[id = "{}"]'.format(node['data']['id']),
        "style": {
            "border-width": 2,
            "border-opacity": 1,
            "opacity": 1,
            "label": "data(label)",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999,
            'font-size': font_size
        }
    }]

    for edge in node['edgesData']:
        if edge['source'] == node['data']['id']:
            focus_stylesheet.append({
                "selector":
                'node[id = "{}"]'.format(edge['target']),
                "style": {
                    'opacity': 0.9
                }
            })
            focus_stylesheet.append({
                "selector":
                'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "line-color": follower_color,
                    'opacity': 0.9,
                    'z-index': 5000
                }
            })

        if edge['target'] == node['data']['id']:
            focus_stylesheet.append({
                "selector":
                'node[id = "{}"]'.format(edge['source']),
                "style": {
                    'opacity': 0.9,
                    'z-index': 9999
                }
            })
            focus_stylesheet.append({
                "selector":
                'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "line-color": follower_color,
                    'opacity': 1,
                    'z-index': 5000
                }
            })
    focus_stylesheet.extend(get_color_stylesheet())
    return focus_stylesheet


if __name__ == '__main__':
    app.run_server(debug=True)
