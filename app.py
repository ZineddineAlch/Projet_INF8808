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


# ------------- Layout -------------#
app.layout = html.Div(
    id="main-div",
    children=[
        # Logo AlayaCare
        html.Img(
            id="alayacare-logo",
            src="./assets/image_alaya.png"
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
                                
                                    style_data={'whiteSpace': 'normal',
                                                'height': 'auto','color':'#08193e','fontWeight': 'bold' },
                                    style_header={
                                        'backgroundColor': '#fafcff', 'fontWeight': 'bold', 'textAlign': 'center', "padding": '10px',
                                        "font-family": "Calibre,Poppins,Roboto,sans-serif",'color':"#ffaa05"},
                                    markdown_options={'html': True},
                                    style_cell={
                                        'textAlign': 'center','font-family': 'Calibre,Poppins,Roboto,sans-serif',"font-size": "18px", "padding":"20px"
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {'state': 'active'},
                                            'backgroundColor': 'rgba(243,112,33,.1)',  # Change the background color of the selected cell
                                            'color': 'rgb(8, 25, 62)',  # Change the text color of the selected cell
                                            'border': '2px solid rgb(211, 211, 211)'
                                            
                                        }
                                    ],
                                )
                            ]
                        ),
                        html.Div(
                                # Table Stats
                                id="table-stats",style={'textAlign': 'center', 'display': 'flex',
                                                        'align-items': 'center'},
                                
                                
                        ),
                        # Detailed view container
                        html.Div(
                            id="detailed-view-container",
                            children=[
                                # Detailed view
                                html.Div(id="calendar-container"),
                                # Summary section and notes
                                html.Div(
                                    id="summary-section-and-notes",
                                    children=[
                                        # Notes
                                        html.Div(
                                            id="note-section",
                                            children=[
                                                html.H3("Note Section"),
                                                html.P("Click on a note to display its content")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
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
                                html.P("9"),
                                html.P("Patients"),
                            ]),
                            html.Div(children=[
                                html.P("8"),
                                html.P("Falls"),
                            ]),
                            html.Div(children=[
                                html.P("6"),
                                html.P("Hospitalizations"),
                            ]),
                            html.Div(children=[
                                html.P("13"),
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
    Output('note-section', 'style'),
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
        if selected_patient == new_selected_patient:
            return dash.no_update
        else:
            selected_patient = new_selected_patient
            schedule_data = preprocess.get_schedule_for_patient(df_timeline, selected_patient)
            note_data = preprocess.get_notes(df_notes, selected_patient)
            radar_chart = vis.get_chart_from_name(selected_patient, mycharts)

            return cal.get_cal(schedule_data,note_data), {"display": "block", "border": "2px solid #ffaa05"}, radar_chart  # Show the note section with the desired styling

    return None, {"display": "none"}, None  # Hide the note section when no cell is selected

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



