import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import preprocess
import vis
import template
import cal

app = dash.Dash(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Project | INF8808'

df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')
df_notes = pd.read_csv('./assets/data/notes.csv')

# -------------   Preprocess results ------------------#

data = preprocess.id_extract(df_timeline)
data[['Completed ADLS', 'Completed visits']
     ] = preprocess.completed_adls_visit(df_timeline).values
data['Stats'] = [
    '<img src="./assets/radar_chart.png" style="width:50px;height:50px;">'
] * len(data)

columns_table1 = preprocess.table1_header()
columns_table2 = preprocess.table2_header()
global_data = preprocess.get_global_data(df_timeline)
schedule_data = preprocess.get_schedule_for_patient(
    df_timeline, "Félix Leclerc")


# ------------- Layout -------------#

app.layout = html.Div(
    children=[
        # Logo AlayaCare
        html.H1(className="text-center", style={"margin": "0px"}, children=[
            html.Img(src="./assets/image_alaya.png",
                     style={"width": "300px", "height": "auto", "margin-top": "20px", "margin-bottom": "20px"})
        ]),
        # Search bar
        html.Div(
            [
                # search bar input
                html.Div(
                    [
                        dcc.Input(
                            id='first-name-input',
                            type='text',
                            placeholder='Search for a patient...',
                            debounce=True,
                            style={
                                'width': '100%',
                                'padding': '10px',
                                'border': '1px solid #ccc',
                                'borderRadius': '5px',
                                'fontFamily': 'Arial',
                                'fontSize': '14px',
                            }
                        ),
                    ], style={"flex": "1", "margin-right": "5px"}
                ),
                # search bar button
                html.Div(
                    [
                        dbc.Button("Search", color="primary",
                                   className="me-1", style={"margin": "0px", "height": "100%"})
                    ],
                    style={"height": "100%"}
                ),
                html.Div(id="output-div"),
            ],
            style={"width": "50%", "display": "flex",
                   "align-items": "center", "margin-bottom": "20px"}
        ),
        # Table 1
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dash_table.DataTable(
                                id='table1',
                                columns=columns_table1,
                                data=data.to_dict('records'),
                                page_size=5,
                                style_table={'overflowX': 'auto'},
                                style_as_list_view=True,
                                style_data={'whiteSpace': 'normal',
                                            'height': 'auto', },
                                style_header={
                                    'backgroundColor': '#ffaa05', 'fontWeight': 'bold', 'textAlign': 'center', "padding": '15px', "color": "white"},
                                selected_rows=[],
                                markdown_options={'html': True},
                                row_selectable=False,
                                style_cell={
                                    'textAlign': 'center',
                                },
                                style_data_conditional=[
                                    {"if": {"column_id": "Stats"}, "background-image": "var(--image-url)", "width": "200px"}],
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            html.Div(id="calendar-container"),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
            ],
            style={"backgroud-color": "red"}
        ),

    ], style={"padding": "20px"})


# ------------------------ Callback -----------------------#

@app.callback(
    Output('calendar-container', 'children'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')]
)
def update_calendar(active_cell, table1_data):
    if active_cell:
        row = active_cell['row']
        selected_patient = table1_data[row]['First Name'] + \
            " " + table1_data[row]['Last Name']
        schedule_data = preprocess.get_schedule_for_patient(
            df_timeline, selected_patient)
        return cal.get_cal(schedule_data)

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