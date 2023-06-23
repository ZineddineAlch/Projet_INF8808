import dash
from dash import html
from dash import dcc,ctx
from dash.dependencies import Input, Output, State ,ALL
import pandas as pd
from dash import dash_table
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

data["Name"] = data[["First Name", 'Last Name']].apply(" ".join, axis=1)

columns_table1 = preprocess.table1_header()
columns_table2 = preprocess.table2_header()
global_data = preprocess.get_global_data(df_timeline)


# ------------- Layout -------------#
note_ids = []

app.layout = html.Div(
    children=[
        # Logo AlayaCare
        html.H1(className="text-center", style={"margin": "0px"}, children=[
            html.Img(src="./assets/image_alaya.png",
                     style={"width": "300px", "height": "auto", "margin-top": "20px", "margin-bottom": "20px"})
        ]),
        # Search bar
        html.H4("Summary of the past 28 days", style={"margin-bottom": "20px"}),
        html.Div(
            [
                # search bar input
                html.Div(
                    [
                        dcc.Input(
                            id='name-input',
                            type='text',
                            placeholder='Search for a patient...',
                            value="",
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
                   "align-items": "center", "margin-bottom": "10px"}
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
                                page_size=8,
                                style_table={'overflowX': 'auto'},
                                style_as_list_view=True,
                                style_data={'whiteSpace': 'normal',
                                            'height': 'auto', },
                                style_header={
                                    'backgroundColor': '#ffaa05', 'fontWeight': 'bold', 'textAlign': 'center', "padding": '15px', "color": "white"},
                                markdown_options={'html': True},
                                style_cell={
                                    'textAlign': 'center',
                                },
                                style_data_conditional=[
                                    {"if": {"column_id": "Stats"}, "background-image": "var(--image-url)", "width": "200px"}],
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            id="calendar-container",
                                            style={"width": "100%", "float": "left", "padding-right": "10px"}
                                        ),
                                        width=11,
                                    ),
                                    dbc.Col(
                                        html.Div(
                                           [
                                                html.Div(
                                                    id="note-content",
                                                    className="note-content",  
                                                ),
                                            ]),
                                        width=3,
                                    ),
                                ],
                                justify="between",
                                style={"display": "flex", "flex-wrap": "nowrap"}
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
            ],
        ),
        #Summary section
        html.Div(
            style={"border": "1px solid #ffaa05", "border-radius": "10px", "width": "50%", "padding": "20px", "display": "flex", "align-items": "center"},
            children = [
                html.Div(children=[
                    html.Span("A", style={"color": "#ffaa05", "font-weight": "bold", "font-size": "36px"}),
                    html.Span("layaCare", style={"color": "#113cca", "font-weight": "bold", "font-size": "36px"}),
                    html.Br(),
                    html.H4("In the past 28 days"),
                ],
                style={"margin-right": "50px"}),
                html.Div(children=[
                    html.Div(children=[
                        html.P("6", style={"font-weight": "bold"}),
                        html.P("Patients", style={"font-weight": "bold"}),
                    ]),
                    html.Div(children=[
                        html.P("6", style={"font-weight": "bold"}),
                        html.P("Falls", style={"font-weight": "bold"}),
                    ]),
                    html.Div(children=[
                        html.P("6", style={"font-weight": "bold"}),
                        html.P("Hospitalizations", style={"font-weight": "bold"}),
                    ]),
                    html.Div(children=[
                        html.P("6", style={"font-weight": "bold"}),
                        html.P("Cancelations", style={"font-weight": "bold"}),
                    ]),
                ],style={"display": "flex", "align-items": "center", "justify-content": "center", "justify-items": "space-beetween"})
            ]
        ),
    ], style={"padding": "20px"}
)


# ------------------------ Callback -----------------------#
selected_patient = None  # Initially, no patient is selected
@app.callback(
    Output('calendar-container', 'children'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')],
)
def update_calendar(active_cell, table1_data):
    global selected_patient

    
    if active_cell:
        row = active_cell['row']
        new_selected_patient  = table1_data[row]['First Name'] + \
            " " + table1_data[row]['Last Name']
        # Check if the selected patient is different from the previously selected one
        if new_selected_patient == None:
            selected_patient = new_selected_patient
            schedule_data = preprocess.get_schedule_for_patient(
                df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            return cal.get_cal(schedule_data,note_data)
        if selected_patient != new_selected_patient:
            selected_patient = new_selected_patient
            schedule_data = preprocess.get_schedule_for_patient(
                df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            return cal.get_cal(schedule_data,note_data)
        if selected_patient == new_selected_patient:
            schedule_data = preprocess.get_schedule_for_patient(
                df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            return dash.no_update

    return None  # Hide the note section when no cell is selected


@app.callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='name-input', component_property='value')
)
def update_table1_data(name):
    # Perform search logic here and return the filtered data for Table 1
    if name == "":
        return data.to_dict('records')
    else:
        return data[data["Name"].str.contains(name)].to_dict('records')
    
@app.callback(
    Output('note-content', 'children'),
    Input({'type':'button_image', 'index':ALL}, 'n_clicks'),
)
def update_content(n_clicks_list):
    global first_time_clicked_note
    try:
        if ctx.triggered_id is not None:
            first_time_clicked_note = False
            for n_click in n_clicks_list:
                if n_click is not None:
                   first_time_clicked_note = True
            if first_time_clicked_note:
                index = int(ctx.triggered_id["index"])
                return cal.retrieve_saved_content_note(index)
            if not first_time_clicked_note:
                return cal.default_content()
        
    except TypeError:
        pass
      
@app.callback(
    Output('note-content', 'style'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')]
    
)
def update_note(active_cell, table1_data):

    if active_cell:
        return {'display': 'block',  # Change 'none' to 'block' to make it visible
            'background': 'repeating-linear-gradient(45deg, rgba(139, 69, 19, 0.2), rgba(139, 69, 19, 0.2) 5px, rgba(233, 236, 239, 0.2) 5px, rgba(233, 236, 239, 0.2) 10px)',
            'border': '2px solid #8B4513',
            'border-radius': '10px',
            'padding': '10px',
            'margin-top': '10px'
            }  # Hide the note section when no cell is selected
    return {'display': 'none',  # Change 'none' to 'block' to make it visible
            'background': 'repeating-linear-gradient(45deg, rgba(139, 69, 19, 0.2), rgba(139, 69, 19, 0.2) 5px, rgba(233, 236, 239, 0.2) 5px, rgba(233, 236, 239, 0.2) 10px)',
            'border': '2px solid #8B4513',
            'border-radius': '10px',
            'padding': '10px',
            'margin-top': '10px'
            }  # Hide the note section when no cell is selected



