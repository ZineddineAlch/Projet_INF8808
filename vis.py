import plotly.graph_objects as go
import pandas as pd
import preprocess
import dash_core_components as dcc

# Read the dataset
df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')
data = preprocess.id_extract(df_timeline)
data["Name"] = data[["First Name", 'Last Name']].apply(" ".join, axis=1)
# Data for the radar chart
CATEGORIES = ['FALL_COUNT', 'CANCELLATION_COUNTS', 'HOSPITALIZATION_COUNT', 'HAS_PAIN_MENTION']

def get_radar_chart(patient_names):

    # Get the aggregated values for the radar chart
    aggregated = df_timeline.groupby('PATIENT_ID').agg({
        'FALL_COUNT': 'sum',
        'CANCELLATION_COUNTS': 'sum',
        'HOSPITALIZATION_COUNT': 'sum',
        'HAS_PAIN_MENTION': 'sum'

    })

    charts = []

    for patient_name in patient_names:

        values = aggregated.loc[patient_name]
        values.values
        # Create a trace for the radar chart
        trace = go.Scatterpolar(
            r=values.values,
            theta=CATEGORIES,
            fill='toself',
            name=patient_name,
            line=dict(color='#113cca'),  # Change the line color to red
            line_shape='spline'
        )
        # Create the layout for the chart
        layout = go.Layout(
            polar=dict(
                radialaxis=dict(visible=True),
                angularaxis=dict(direction='counterclockwise', rotation=45) 
            ),
            
            showlegend=False,
            height=350,  # Set the height of the chart (in pixels)
            width=550,  # Set the width of the chart (in pixels)
            margin=dict(l=50, r=50, t=50, b=50)  # Set the margins around the chart

        )
        # Create the figure and add the trace
        fig = go.Figure(data=[trace], layout=layout)
        charts.append([fig, patient_name])
    return charts

mycharts = get_radar_chart(data["Name"])

def get_chart_from_name(name, charts):
    for chart in charts:
        if chart[1] == name:
            return dcc.Graph(figure=chart[0])