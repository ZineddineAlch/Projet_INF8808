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
img='<img src="./assets/radar_chart.png" >'
data["Name"] = data[["First Name", 'Last Name']].apply(" ".join, axis=1)

data_stats = pd.DataFrame({'Stats': ['<img src="./assets/radar_chart.png" width="450" height="490">']}) * 0

mycharts = vis.get_radar_chart(data["Name"])

columns_table1 = preprocess.table1_header()
columns_table2 = preprocess.table2_header()
global_data = preprocess.get_global_data(df_timeline)
summary = preprocess.calculate_summary(df_timeline)

# ------------- Layout -------------#
app.layout = html.Div(
    id="main-div",
    children=[
        # Logo AlayaCare
        html.Img(
            id="alayacare-logo",
            src="./assets/image_alaya.png",
        ),
        html.Div(
            id="parent-div",
            children=[
                # Content container div
                html.Div(
                    id="container-div",
                    children=[
                        # Global view
                        html.Div(
                            id="global-view",
                            children=[
                                # header
                                html.H4("Summary of the past 28 days"),
                                # Search bar
                                html.Div(
                                    id="search-bar",
                                    children=[
                                        dcc.Input(
                                            id='name-input',
                                            type='text',
                                            placeholder='Search for a patient...',
                                            value="",
                                            debounce=True
                                            ),
                                        dbc.Button("Search")
                                    ]
                                ),
                                # Table
                                dash_table.DataTable(
                                    id='table1',
                                    columns=columns_table1,
                                    data=data.to_dict('records'),
                                    page_size=8,
                                    style_table={'overflowX': 'auto'},
                                    style_as_list_view=True,
                                    sort_action='native',
                                    sort_mode='single',
                                    column_selectable = 'multi',
                                    style_data={'whiteSpace': 'normal',
                                                'height': 'auto','color':'#08193e','fontWeight': 'bold' },
                                    style_header={
                                        'backgroundColor': '#fafcff', 'fontWeight': 'bold', 'textAlign': 'center', "padding": '10px',
                                        "font-family": "Calibre,Poppins,Roboto,sans-serif",'color':"#ffaa05"},
                                    markdown_options={'html': True},
                                    style_cell={
                                        'textAlign': 'center','font-family': 'Calibre,Poppins,Roboto,sans-serif',"font-size": "16px", "padding":"15px"
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {'state': 'active'},
                                            'backgroundColor': 'rgba(243,112,33,.1)',  # Change the background color of the selected cell
                                            'color': 'rgb(8, 25, 62)',  # Change the text color of the selected cell
                                            'border': '2px solid rgb(211, 211, 211)'
                                            
                                        }
                                    ],
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'Name'},
                                        'width': '50%'},
                                        {'if': {'column_id': 'Completed visits'},
                                        'width': '25%'},
                                    ],
                                )
                            ]
                        ),
                        # Detailed view container
                        html.Div(
                            id="detailed-view-container",
                            children=[
                                # Detailed view
                                html.Div(id="calendar-container"),
                                html.Div(
                                    id="legend",
                                    children=[
                                        html.H3("Legend"),
                                        html.Div(
                                            style={

                                                "gap": "20px",
                                            },
                                            children=[
                                                html.Div(
                                                    style={"display": "flex", "flex-direction": "row", "align-items": "center","justify-content":"space-between"},
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.Img(src="assets/pain.png", style={"max-width": "20%"}),
                                                                html.P("Pain"),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Img(src="assets/fall1.png", style={"max-width": "20%"}),
                                                                html.P("Fall"),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Img(src="assets/note.jpeg", style={"max-width": "20%"}),
                                                                html.P("Note"),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Img(src="assets/hospital.png", style={"max-width": "20%"}),
                                                                html.P("Hospitalization"),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Img(src="assets/cancelled.png", style={"max-width": "20%"}),
                                                                html.P("Cancellation"),
                                                            ],
                                                        ),
                                                        
                                                    ]
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        html.Div(
                            id="stats-notes",
                            style={"display": "flex", "flex-direction": "column"},
                            children=[
                                html.Div(
                                    # Table Stats
                                    id="table-stats",style={'display': 'flex', "flex-direction": "column", 'text-align': 'center', "height": "fit-content"},
                                ),
                                html.Div(
                                    id="note-section",
                                    style={"text-align": "center"},
                                    children=[
                                        html.H3("Note Section"),
                                        html.P("Click on a note to display its content")
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
                # Footer
                html.Div(
                    id="footer-section",
                    children = [
                        html.Div(
                            id="left-footer-section",
                            children=[
                            html.Span("A", style={"color": "#ffaa05", "font-weight": "bold", "font-size": "36px"}),
                            html.Span("layaCare", style={"color": "#113cca", "font-weight": "bold", "font-size": "36px"}),
                            html.Br(),
                            html.H4("In the past 28 days"),
                        ]),
                        html.Div(
                            id="right-footer-section",
                            children=[
                            html.Div(children=[
                                html.P(summary['Patients']),
                                html.P("Patients"),
                            ]),
                            html.Div(children=[
                                html.P(summary['Falls']),
                                html.P("Falls"),
                            ]),
                            html.Div(children=[
                                html.P(summary['Hospitalizations']),
                                html.P("Hospitalizations"),
                            ]),
                            html.Div(children=[
                                html.P(summary['Cancelations']),
                                html.P("Cancelations"),
                            ]),
                        ])
                    ]
                )
            ],
        ),
    ]
)

# ------------------------ Callback -----------------------#
selected_patient = None  # Initially, no patient is selected
@app.callback(
    Output('calendar-container', 'children'),
    Output('stats-notes', 'style'),
    Output('table-stats', 'children'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')],
)
def update_calendar(active_cell, table1_data):
    print('active cell : ', active_cell)
    
    global selected_patient

    if active_cell:
        row = active_cell['row']
        new_selected_patient  = table1_data[row]['First Name'] + \
            " " + table1_data[row]['Last Name']
        print('new patient : ', new_selected_patient)

        # Check if the selected patient is different from the previously selected one
        '''if selected_patient == new_selected_patient:
            return dash.no_update'''
        if new_selected_patient != None:
            selected_patient = new_selected_patient
            schedule_data = preprocess.get_schedule_for_patient(df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            stats_children = [html.H3("Last 28 days (normalized)", style={'color': 'rgb(255, 170, 5)','text-align':'center'}), vis.get_chart_from_name(selected_patient, mycharts)]
            cal_children = [html.H1(selected_patient, style={'color': '#113cca','font-size':'24px', 'text-align': 'left','fontWeight': 'bold'}), cal.get_cal(schedule_data,note_data)]
            return cal_children, {"display": "flex", "flex-direction": "column"}, stats_children  # Show the note section with the desired styling

    return None, {"display": "none"}, None  # Hide the note section when no cell is selected



@app.callback(
    Output('legend', 'style'),
    [Input('table1', 'active_cell')],
    [State('table1', 'data')],
)
def update_calendar(active_cell, table1_data):
    print('active cell : ', active_cell)
    
    global selected_patient

    if active_cell:
        row = active_cell['row']
        new_selected_patient  = table1_data[row]['First Name'] + \
            " " + table1_data[row]['Last Name']
        if new_selected_patient != None:
            return {"display":"flex"}

    return None  # Hide the note section when no cell is selected

@app.callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='name-input', component_property='value')
)
def update_table1_data(name):
    # Perform search logic here and return the filtered data for Table 1
    dic = dict()
    for i in vis.all_patients_area:
        dic.update({i.index[0] :i[0]})
    dic = sorted(dic.items(), key=lambda x:x[1], reverse=True)
    data_aux = pd.DataFrame(columns=['Name', 'patient_radar_area'], data=dic)
    data_aux = pd.merge(data_aux, data, on='Name')
    if name == "":
        return data_aux.to_dict('records')
    else:
        return data_aux[data_aux["Name"].str.lower().str.contains(name.lower())].to_dict('records')
    
    
@app.callback(
    Output('note-section', 'children'),
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



