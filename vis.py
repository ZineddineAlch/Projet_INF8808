import plotly.graph_objects as go
import pandas as pd

# Data for the radar chart
CATEGORIES = ['FALL_COUNT', 'CANCELLATION_COUNTS', 'HOSPITALIZATION_COUNT', 'HAS_PAIN_MENTION']

def get_radar_chart(patient_names):
    # Read the dataset
    df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')

    # Get the aggregated values for the radar chart
    aggregated = df_timeline.groupby('PATIENT_ID').agg({
        'FALL_COUNT': 'sum',
        'CANCELLATION_COUNTS': 'sum',
        'HOSPITALIZATION_COUNT': 'sum',
        'HAS_PAIN_MENTION': 'sum'
    })

    charts = []
    for patient_name in patient_names:
        
        # Get the values for the radar chart
        values = aggregated.loc[patient_name]
        values.values
        # Create a trace for the radar chart
        trace = go.Scatterpolar(
            r=values,
            theta=CATEGORIES,
            fill='toself'
        )

        # Create the layout for the chart
        layout = go.Layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            showlegend=False
        )

        # Create the figure and add the trace
        fig = go.Figure(data=[trace], layout=layout)
        charts.append([fig, patient_name])
    return charts

mycharts = get_radar_chart(["André Fortin", "Céline Dion"])

def get_chart_from_name(name, charts):
    for chart in charts:
        if chart[1] == name:
            return chart[0]

#chart = get_chart_from_name("André Fortin", mycharts)
#chart.show()