"""
Original Demo: http://js.cytoscape.org/demos/cose-bilkent-layout-compound/

Note: This implementation DOES NOT work yet, since cose-bilkent hasn't been implemented yet

"""
import json

import dash
import dash_html_components as html

import dash_cytoscape as cyto

cyto.load_extra_layouts()
app = dash.Dash(__name__)
server = app.server



# Load Data
with open('data/cose-bilkent-layout/data.json', 'r') as f:
    elements = json.loads(f.read())

# App
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={
            'name': 'cose-bilkent',
            'animate': False
        },
        stylesheet=[{
            'selector': 'node',
            'style': {
                'background-color': '#ad1a66'
            }
        }, {
            'selector': 'edge',
            'style': {
                'width': 3,
                'line-color': '#ad1a66'
            }
        }],

        style={
            'width': '100%',
            'height': '100%',
            'position': 'absolute',
            'left': 0,
            'top': 0,
            'z-index': 999
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
