import dash
from dash import html
from dash import dcc,ctx
from dash.dependencies import Input, Output, State ,ALL
import pandas as pd
from dash import dash_table
import dash_bootstrap_components as dbc
import preprocess
import vis
import cal
import note


app = dash.Dash(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Project | INF8808'

df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')
df_notes = pd.read_csv('./assets/data/notes.csv')

# -------------   Preprocess results ------------------#

data = preprocess.id_extract(df_timeline)
data[['ADLS', 'Visits', 'Pain', 'Fall','Hospitalization']
     ] = preprocess.completed_adls_visit(df_timeline).values

data["Name"] = data[["First Name", 'Last Name']].apply(" ".join, axis=1)
data["id"] = data["Name"]
data_stats = pd.DataFrame({'Stats': ['<img src="./assets/radar_chart.png" width="450" height="490">']}) * 0

mycharts = vis.get_radar_chart(data["Name"])

columns_table1 = preprocess.table1_header()
columns_table2 = preprocess.table2_header()
global_data = preprocess.get_global_data(df_timeline)
summary = preprocess.calculate_summary(df_timeline)


app.layout = html.Div(
    id="main-div",
    children=[
        html.A(
            href="/",
            children=[
                html.Img(
                    id="alayacare-logo",
                    src="./assets/image_alaya.png",
                ),
            ]
        ),
        html.Div(
            id="parent-div",
            children=[
                html.Div(
                    id="container-div",
                    children=[
                        html.Div(
                            id="global-view",
                            children=[
                                html.H4("Summary of the past 28 days"),
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
                                            'backgroundColor': 'rgba(243,112,33,.1)',  
                                            'color': 'rgb(8, 25, 62)',  
                                            'border': '2px solid rgb(211, 211, 211)'
                                        }
                                    ],
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'Name'},
                                        'width': '300px'},
                                        {'if': {'column_id': 'Completed visits'},
                                        'width': '25%'},
                                    ],
                                ),
                                html.Div(
                                    id="footer-section",
                                    children = [
                                        html.Div(
                                            id="left-footer-section",
                                            children=[
                                            html.Span("A", style={"color": "#ffaa05", "font-weight": "bold", "font-size": "24px"}),
                                            html.Span("layaCare", style={"color": "#113cca", "font-weight": "bold", "font-size": "24px"}),
                                            html.Br(),
                                            html.H4("In the past 28 days",style={"font-size": "24px"}),
                                        ]),
                                        html.Div(
                                            id="right-footer-section",
                                            children=[
                                            html.Div(children=[
                                                html.P(summary['Patients'],style={"font-size": "19px"}),
                                                html.P("Patients",style={"font-size": "19px"}),
                                            ]),
                                            html.Div(children=[
                                                html.P(summary['Falls'],style={"font-size": "19px"}),
                                                html.P("Falls",style={"font-size": "19px"}),
                                            ]),
                                            html.Div(children=[
                                                html.P(summary['Hospitalizations'],style={"font-size": "19px"}),
                                                html.P("Hospitalizations",style={"font-size": "19px"}),
                                            ]),
                                            html.Div(children=[
                                                html.P(summary['Cancelations'],style={"font-size": "19px"}),
                                                html.P("Cancelations",style={"font-size": "19px"}),
                                            ]),
                                        ])
                                    ]
                                ),
                            ],
                        ),
                        
                        html.Div(
                            id="detailed-view-container",
                            children=[
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
                            children=[
                                html.Div(
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
            ],
        ),
    ]
)

# ------------------------ Callback -----------------------#
selected_patient = None 
active_page = None
@app.callback(
    Output('calendar-container', 'children'),
    Output('stats-notes', 'style'),
    Output('table-stats', 'children'),
    Output('legend', 'style'),
    Output('table1', 'columns'), 
    Output('global-view', 'style'),
    [Input('table1', 'active_cell')],
    [Input('table1', 'page_current')],
    [State('table1', 'data')],
)
def update_calendar(active_cell, page_current, table1_data):
    if page_current is None and active_cell is not None:
        page_current = 0
    global selected_patient
    global active_page

    if active_cell:
        active_page = page_current
        new_selected_patient = active_cell['row_id']
        columns_table1_updated = [col for col in preprocess.table1_header() if col['id'] not in ['Pain', 'Fall','Hospitalization']] 
        global_view_style = {"width": "27%"}
        if new_selected_patient != None:
            selected_patient = new_selected_patient
            schedule_data = preprocess.get_schedule_for_patient(df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            stats_children = create_stats_children(selected_patient)
            stats_style = {"display": "flex", "flex-direction": "column"}
            cal_children = create_cal_children(selected_patient, schedule_data, note_data)
            legend_style = {"display":"flex"}
        return cal_children, stats_style, stats_children, legend_style, columns_table1_updated, global_view_style
    elif page_current is not None:
        active_page = page_current
        return dash.no_update
    global_view_style = {"width": "50%"}
    return None, {"display": "none"}, None, None, preprocess.table1_header(), global_view_style

def create_stats_children(selected_patient):
    return [
        html.H3("Last 28 days (normalized)", style={'color': 'rgb(255, 170, 5)', 'text-align': 'center'}),
        html.P("Hover on a point to see the total number for a metric.", style={"width": "min-content", "min-width": "100%", "font-size": "15px"}),
        vis.get_chart_from_name(selected_patient, mycharts)
    ]

def create_cal_children(selected_patient, schedule_data, note_data):
    return [
        html.H3(selected_patient, style={'color': '#113cca', 'text-align': 'left', 'fontWeight': 'bold'}),
        cal.get_cal(schedule_data, note_data)
    ]

@app.callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='name-input', component_property='value')
)
def update_table1_data(name):
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
            first_time_clicked_note = check_first_time_clicked(n_clicks_list)
            if first_time_clicked_note:
                index = get_triggered_index()
                return note.retrieve_saved_content_note(index)
            if not first_time_clicked_note:
                return note.default_content()
        
    except TypeError:
        pass
def check_first_time_clicked(n_clicks_list):
    first_time_clicked_note = False
    for n_click in n_clicks_list:
        if n_click is not None:
            first_time_clicked_note = True
    return first_time_clicked_note

def get_triggered_index():
    return int(ctx.triggered_id["index"])



