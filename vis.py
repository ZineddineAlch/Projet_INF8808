import plotly.graph_objects as go
import pandas as pd
import numpy as np
import shapely
import preprocess
from dash import dcc
import numpy as np
from preprocess import get_global_data

# Read the dataset
df_timeline = pd.read_csv('./assets/data/timeline_dataset.csv')
data = preprocess.id_extract(df_timeline)
data["Name"] = data[["First Name", 'Last Name']].apply(" ".join, axis=1)
# Data for the radar chart
CATEGORIES = ['CANCELLATION_COUNTS', 'FALL_COUNT', 'HOSPITALIZATION_COUNT', 'HAS_PAIN_MENTION']



def get_radar_chart(patient_names):
    # Get the aggregated values for the radar chart
    aggregated = df_timeline.groupby('PATIENT_ID').agg({
        'CANCELLATION_COUNTS': 'sum',
        'FALL_COUNT': 'sum',
        'HOSPITALIZATION_COUNT': 'sum',
        'HAS_PAIN_MENTION': 'sum'
    })

    max_cancel, min_cancel = aggregated["CANCELLATION_COUNTS"].values.max(), aggregated["CANCELLATION_COUNTS"].values.min()
    max_fall, min_fall = aggregated["FALL_COUNT"].values.max(), aggregated["FALL_COUNT"].values.min()
    max_hosp, min_hosp = aggregated["HOSPITALIZATION_COUNT"].values.max(), aggregated["HOSPITALIZATION_COUNT"].values.min()
    max_pain, min_pain = aggregated["HAS_PAIN_MENTION"].values.max(), aggregated["HAS_PAIN_MENTION"].values.min()

    aggregated_norm = aggregated.copy(deep=True)
    aggregated_norm['CANCELLATION_COUNTS'] = (aggregated_norm['CANCELLATION_COUNTS'] - min_cancel) / (max_cancel - min_cancel)
    aggregated_norm['FALL_COUNT'] = (aggregated_norm['FALL_COUNT'] - min_fall) / (max_fall - min_fall)
    aggregated_norm['HOSPITALIZATION_COUNT'] = (aggregated_norm['HOSPITALIZATION_COUNT'] - min_hosp) / (max_hosp - min_hosp)
    aggregated_norm['HAS_PAIN_MENTION'] = (aggregated_norm['HAS_PAIN_MENTION'] - min_pain) / (max_pain - min_pain)

    charts = []
    global all_patients_area
    all_patients_area = []
    for patient_name in patient_names:

        norm_values = aggregated_norm.loc[patient_name].values
        values = aggregated.loc[patient_name].values

        # Create a trace for the radar chart
        trace = go.Scatterpolar(
            r=norm_values,
            theta=CATEGORIES,
            fill='toself',
            name=patient_name,#f"<b>{patient_name}</b><br><ul><li>Cancellations: {values[0]}</li> <li>Falls: {values[1]}</li> <li>Hospitalizations: {values[2]}</li> <li>Pain mentions: {values[3]}</li></ul>",
            line=dict(color='#113cca'),  # Change the line color to red
            line_shape='spline',
            customdata=values,
            hovertemplate='<b>%{theta}:</b> %{customdata}' + '<extra></extra>',
        )
        # Create the layout for the chart
        layout = go.Layout(
            font=dict(
                family="Calibre, Poppins, Roboto, sans-serif",
                size=14,
                color="#113cca"),
            polar=dict(
                radialaxis=dict(visible=True, showticklabels=False, range=[0,1]),
                angularaxis=dict(direction='counterclockwise',
                                 rotation=90,
                                 dtick=45,
                                 tickmode="array",
                                 showticklabels=True,
                                 tickvals=CATEGORIES,
                                 ticktext=["Cancellations", "Falls", "Hospitalizations", "Pain"],) 
            ),

            showlegend=False,
            height=350,  # Set the height of the chart (in pixels)
            width=350,  # Set the width of the chart (in pixels)
            margin=dict(l=50, r=50, t=50, b=50)  # Set the margins around the chart
        )
        # Create the figure and add the trace
        fig = go.Figure(data=[trace], layout=layout)
        charts.append([fig, patient_name])
        # get data back out of figure
        df = pd.concat([
            pd.DataFrame({"r": t.r, "theta": t.theta, "trace": np.full(len(t.r), t.name)})
            for t in fig.data
            ]
                       )
        # convert theta to be in radians
        df["theta_n"] = pd.factorize(df["theta"])[0]
        df["theta_radian"] = (df["theta_n"] / (df["theta_n"].max() + 1)) * 2 * np.pi
        # work out x,y co-ordinates
        df["x"] = np.cos(df["theta_radian"]) * df["r"]
        df["y"] = np.sin(df["theta_radian"]) * df["r"]
        # generate a polygon from co-ordinates using shapely
        # get the area of the polygon
        df_a = df.groupby("trace").apply(
            lambda d: shapely.geometry.MultiPoint(list(zip(d["x"], d["y"]))).convex_hull.area)
        # let's use the areas in the name of the traces
        fig.for_each_trace(lambda t: t.update(name=f"{t.name} {df_a.loc[t.name]:.1f}"))
        #print(type(df_a))
        all_patients_area.append(df_a)
    #print(all_patients_area)
    return charts

mycharts = get_radar_chart(data["Name"])

def get_chart_from_name(name, charts):
    for chart in charts:
        if chart[1] == name:
            return dcc.Graph(figure=chart[0])

def fall_pain_hosplot(df):
  
    df = get_global_data(df)
    df = df[['FALL_COUNT', 'HAS_PAIN_MENTION', 'HOSPITALIZATION_COUNT']]
    df['color'] = ['rgb{}'.format((np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255))) for _ in range(df.shape[0])]
    fig = go.Figure()

    
    for i in range(df.shape[0]):
        fig.add_trace(go.Scatter(
            x=df.columns[:-1], 
            y=df.iloc[i][:-1], 
            mode='lines',
            line=dict(color=df.iloc[i]['color']), 
            name=df.index[i]  
        ))

    return fig

def visites_bar_chart(df):
    df = get_global_data(df)
    assert 'VISIT_COUNTS' in df.columns, "Le DataFrame doit contenir une colonne 'VISIT_COUNTS'."
    assert 'CANCELLATION_COUNTS' in df.columns, "Le DataFrame doit contenir une colonne 'CANCELLATION_COUNTS'."

    x_values = df.index

    fig = go.Figure(data=[
        go.Bar(name='VISIT_COUNTS', x=x_values, y=df['VISIT_COUNTS'], marker_color='green'),
        go.Bar(name='CANCELLATION_COUNTS', x=x_values, y=df['CANCELLATION_COUNTS'], marker_color='red')
    ])


    fig.update_layout(barmode='group')

    return fig
