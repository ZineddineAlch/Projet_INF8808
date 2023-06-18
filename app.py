import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc

import preprocess
import vis
import template
import cal

app = dash.Dash(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Project | INF8808'

df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')
df_notes = pd.read_csv('./assets/data/notes.csv')

#-------------   Preprocess results ------------------#

data = preprocess.id_extract(df_timeline)
columns_table1 = preprocess.table1_header()
columns_table2 = preprocess.table2_header()

#------------- Layout -------------#

app.layout = html.Div(
    children=[
        html.H1("AlayaCare", className="title is-1", style={"textAlign": "center"}),
        html.Img(src="image_alaya.png"),
        html.Hr(),
        html.P("Enter patient name:"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Input(
                            id='first-name-input',
                            type='text',
                            placeholder='Enter first name...',
                            debounce=True,
                        ),
                    ],
                    style={"display": "inline-block", "marginRight": "10px"},
                ),
                html.Div(
                    [
                        dcc.Input(
                            id='last-name-input',
                            type='text',
                            placeholder='Enter last name...',
                            debounce=True,
                        ),
                    ],
                    style={"display": "inline-block", "marginRight": "10px"},
                ),
                html.Div(id="output-div"),
            ],
            className="row",
        ),
        html.Div(
            [
                html.Div(
                    [
                        # Adding the table using DataTable
                        dash_table.DataTable(
                            id='table1',
                            columns=columns_table1,
                            data=data.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_data={'textAlign': 'center'},
                            style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold', 'textAlign': 'center'},
                            selected_rows=[],
                            row_selectable=False
                        ),
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                       cal.get_cal()
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div(style={"margin-bottom": "20px"}),
        html.Div(
            [
                html.Div(
                    [
                        # Adding the table using DataTable
                        dash_table.DataTable(
                            id='table3',
                            columns=[
                                {"name": "AlyaCare in the past 28 days", "id": "Rien"},
                                {"name": "Patients", "id": "Patients"},
                                {"name": "Falls", "id": "Falls"},
                                {"name": "Hospitalizations", "id": "Hospitalizations"},
                                {"name": "Cancelations", "id": "Cancelations"},
                            ],
                            data=[],
                            style_table={'overflowX': 'auto'},
                            style_data={'textAlign': 'center'},
                            style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold', 'textAlign': 'center'},
                            selected_rows=[],
                            row_selectable=False,
                        ),
                    ],
                    className="four columns",
                )
            ],
            className="row",
        ),
    ]
)

#------------------------ Callback -----------------------#

@app.callback(
    Output('table2', 'data'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')]
)
def update_table2_data(active_cell, table1_data):
    return None

@app.callback(
    Output('table1', 'data'),
    [Input('first-name-input', 'value'),
     Input('last-name-input', 'value')]
)
def update_table1_data(first_name, last_name):
    # Perform search logic here and return the filtered data for Table 1
    if first_name and last_name:
        filtered_data = data[
            (data['First Name'].str.contains(first_name, case=False)) &
            (data['Last Name'].str.contains(last_name, case=False))
        ]
        return filtered_data.to_dict('records')
    else:
        return data.to_dict('records')

